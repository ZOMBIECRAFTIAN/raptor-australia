"""
Australian Raptor CNN — End-to-end retraining script
====================================================
Runs the full pipeline on the *expanded* iNaturalist + ALA dataset:

  1. Discover and validate every image in ``dataset/raw/<species>/``
  2. Split 80/10/10 (stratified, seed=42) → ``dataset/processed/``
  3. Train EfficientNetB4 with two-stage transfer learning:
        - Stage 1 (10 epochs): freeze backbone, train classifier head
        - Stage 2 (20 epochs): unfreeze last 20 layers, low-LR fine-tune
  4. Evaluate on the test split
  5. Persist outputs:
        - models/best_model.pth   (best checkpoint by val_f1)
        - results/reporte_final.json
        - results/test_report.csv
        - results/training_history.csv
        - results/confusion_matrix.png
        - results/learning_curves.png
        - results/f1_por_especie.png

Usage (from project root):
    python notebooks/retrain.py
    python notebooks/retrain.py --skip-preprocess   # use existing splits
    python notebooks/retrain.py --epochs-stage1 5 --epochs-stage2 15
    python notebooks/retrain.py --batch-size 16     # if VRAM allows

    # 4-architecture comparison for the thesis (run sequentially):
    python notebooks/retrain.py --arch efficientnet_b4   --skip-preprocess
    python notebooks/retrain.py --arch resnet50          --skip-preprocess
    python notebooks/retrain.py --arch mobilenet_v3_large --skip-preprocess
    python notebooks/retrain.py --arch convnext_tiny     --skip-preprocess

Each architecture writes:
    models/best_model_<arch>.pth                (or best_model.pth for b4)
    results/reporte_final_<arch>.json           (or reporte_final.json   for b4)

Tested with: Python 3.10, PyTorch 2.x, CUDA 11.8 on RTX 3060.
Approx wall time: ~1.5–2 h on a single GPU for the 5k-image dataset
(per architecture; the 4-arch comparison takes one work day on GPU).
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from PIL import Image, ImageOps
from sklearn.metrics import (classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score,
                             accuracy_score)
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader
from torchvision import datasets, models
from tqdm import tqdm

# ─── Configuration ──────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent.parent
RAW_DIR       = PROJECT_ROOT / "dataset" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "dataset" / "processed"
METADATA_DIR  = PROJECT_ROOT / "dataset" / "metadata"
MODELS_DIR    = PROJECT_ROOT / "models"
RESULTS_DIR   = PROJECT_ROOT / "results"

for d in (MODELS_DIR, RESULTS_DIR, METADATA_DIR):
    d.mkdir(parents=True, exist_ok=True)

IMG_SIZE     = 380
NUM_CLASSES  = 8
TRAIN_RATIO  = 0.80
VAL_RATIO    = 0.10
TEST_RATIO   = 0.10
MIN_DIM      = 224                    # discard images smaller than this
SEED         = 42

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

# Pretty species labels for the confusion-matrix figure
SPECIES_LABELS = {
    "aquila_audax":           "Wedge-tailed Eagle",
    "circus_assimilis":       "Spotted Harrier",
    "elanus_axillaris":       "Black-shouldered Kite",
    "falco_cenchroides":      "Nankeen Kestrel",
    "falco_peregrinus":       "Peregrine Falcon",
    "hieraaetus_morphnoides": "Little Eagle",
    "lophoictinia_isura":     "Square-tailed Kite",
    "tachyspiza_fasciata":    "Brown Goshawk",
}


# ─── Reproducibility ────────────────────────────────────
def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ─── Stage 1: dataset split + preprocess ────────────────
def is_valid_image(path: Path) -> bool:
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            w, h = im.size
            return min(w, h) >= MIN_DIM
    except Exception:
        return False


def preprocess_dataset() -> None:
    """Re-build train/val/test splits from RAW_DIR."""
    print("\n=== STAGE 1 — Preprocessing dataset ===\n")
    if PROCESSED_DIR.exists():
        print(f"Removing old {PROCESSED_DIR} ...")
        shutil.rmtree(PROCESSED_DIR)

    species_keys = sorted(p.name for p in RAW_DIR.iterdir() if p.is_dir())
    print(f"Species discovered: {len(species_keys)}\n")
    print(f"{'species':<28} {'valid':>7} {'train':>7} {'val':>6} {'test':>6}")
    print("-" * 60)

    rows: list[dict] = []
    for sp in species_keys:
        files = list((RAW_DIR / sp).glob("*"))
        valids = [p for p in files if is_valid_image(p)]
        random.Random(SEED).shuffle(valids)
        n = len(valids)
        n_train = int(n * TRAIN_RATIO)
        n_val   = int(n * VAL_RATIO)

        splits = {
            "train": valids[:n_train],
            "val":   valids[n_train:n_train + n_val],
            "test":  valids[n_train + n_val:],
        }
        print(f"{sp:<28} {n:>7} {len(splits['train']):>7} "
              f"{len(splits['val']):>6} {len(splits['test']):>6}")

        for split, paths in splits.items():
            out_dir = PROCESSED_DIR / split / sp
            out_dir.mkdir(parents=True, exist_ok=True)
            for src in tqdm(paths, desc=f"  {sp}/{split}", leave=False):
                try:
                    img = Image.open(src).convert("RGB")
                    img = ImageOps.exif_transpose(img)
                    # Centre-crop to square then resize.
                    w, h = img.size
                    s = min(w, h)
                    left = (w - s) // 2
                    top  = (h - s) // 2
                    img  = img.crop((left, top, left + s, top + s))
                    img  = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
                    img.save(out_dir / src.name, "JPEG", quality=92)
                    rows.append({"species_key": sp, "split": split,
                                 "filename": src.name})
                except Exception as e:
                    print(f"\n  ! skipped {src}: {e}")

    pd.DataFrame(rows).to_csv(METADATA_DIR / "split_indices.csv",
                              index=False)
    print(f"\nSplit log saved to {METADATA_DIR / 'split_indices.csv'}")


# ─── Stage 2: model + training ──────────────────────────
class AustralianRaptorCNN(nn.Module):
    """EfficientNetB4 architecture used by the production GUI."""

    def __init__(self, num_classes: int = NUM_CLASSES,
                 dropout_rate: float = 0.4):
        super().__init__()
        self.backbone = models.efficientnet_b4(
            weights=models.EfficientNet_B4_Weights.IMAGENET1K_V1
        )
        nf = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate, inplace=True),
            nn.Linear(nf, 512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate / 2),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


# ─── Multi-architecture builder (porting Veracruz pattern) ───
def build_model(arch: str = "efficientnet_b4",
                num_classes: int = NUM_CLASSES) -> nn.Module:
    """
    Builds one of four backbones for the 4-architecture comparison
    described in the thesis Chapter 3.4. Mirrors the pattern of the
    author's Veracruz project (raptors-cnn).

    Supported:
        efficientnet_b4   — production default (gui/app.py)
        resnet50          — robust baseline
        mobilenet_v3_large — edge / mobile reference
        convnext_tiny     — state-of-the-art 2022 reference
    """
    arch = arch.lower()
    if arch == "efficientnet_b4":
        return AustralianRaptorCNN(num_classes)

    if arch == "resnet50":
        m = models.resnet50(
            weights=models.ResNet50_Weights.IMAGENET1K_V2)
        m.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(m.fc.in_features, num_classes),
        )
        return m

    if arch == "mobilenet_v3_large":
        m = models.mobilenet_v3_large(
            weights=models.MobileNet_V3_Large_Weights.IMAGENET1K_V2)
        m.classifier[-1] = nn.Linear(
            m.classifier[-1].in_features, num_classes)
        return m

    if arch == "convnext_tiny":
        m = models.convnext_tiny(
            weights=models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1)
        m.classifier[-1] = nn.Linear(
            m.classifier[-1].in_features, num_classes)
        return m

    raise ValueError(f"Unsupported architecture: {arch}")


def get_feature_layers(model: nn.Module, arch: str) -> list:
    """Returns the parameter list of backbone feature layers,
    used by the two-stage training to freeze/unfreeze.
    """
    arch = arch.lower()
    if arch == "efficientnet_b4":
        return list(model.backbone.features.parameters())
    if arch == "resnet50":
        # Conv1 + bn1 + relu + maxpool + layer1-4
        return (list(model.conv1.parameters()) +
                list(model.bn1.parameters()) +
                list(model.layer1.parameters()) +
                list(model.layer2.parameters()) +
                list(model.layer3.parameters()) +
                list(model.layer4.parameters()))
    if arch in ("mobilenet_v3_large", "convnext_tiny"):
        return list(model.features.parameters())
    raise ValueError(f"Unsupported architecture: {arch}")


def make_loaders(batch_size: int):
    train_t = transforms.Compose([
        transforms.Resize((420, 420)),
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3,
                               saturation=0.2, hue=0.1),
        transforms.RandomGrayscale(p=0.05),
        transforms.GaussianBlur(kernel_size=3),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    eval_t = transforms.Compose([
        transforms.Resize((420, 420)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    train_ds = datasets.ImageFolder(str(PROCESSED_DIR / "train"), train_t)
    val_ds   = datasets.ImageFolder(str(PROCESSED_DIR / "val"),   eval_t)
    test_ds  = datasets.ImageFolder(str(PROCESSED_DIR / "test"),  eval_t)

    print(f"  train: {len(train_ds):>5}  | val: {len(val_ds):>4}  "
          f"| test: {len(test_ds):>4}")

    kwargs = dict(batch_size=batch_size, num_workers=0, pin_memory=True)
    return (
        DataLoader(train_ds, shuffle=True, **kwargs),
        DataLoader(val_ds,   shuffle=False, **kwargs),
        DataLoader(test_ds,  shuffle=False, **kwargs),
        train_ds,
    )


def class_weight_tensor(train_ds, device):
    labels = [y for _, y in train_ds.samples]
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(labels),
        y=labels,
    )
    return torch.FloatTensor(weights).to(device)


def evaluate(model, loader, device, class_names):
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            preds = model(x).argmax(1)
            y_true.extend(y.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "report": classification_report(
            y_true, y_pred, target_names=class_names,
            zero_division=0, output_dict=True,
        ),
        "y_true": y_true, "y_pred": y_pred,
    }


def train(epochs_s1: int, epochs_s2: int, batch_size: int,
          lr_s1: float = 1e-3, lr_s2: float = 1e-4,
          arch: str = "efficientnet_b4") -> None:
    print(f"\n=== STAGE 2 — Training ({arch}) ===\n")
    set_seed()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    train_loader, val_loader, test_loader, train_ds = make_loaders(batch_size)
    class_names = train_ds.classes

    model = build_model(arch, NUM_CLASSES).to(device)
    weights = class_weight_tensor(train_ds, device)
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.05)

    history = {"epoch": [], "phase": [], "train_loss": [],
               "train_acc": [], "val_acc": [], "val_f1": []}
    # Per-architecture checkpoint name so multiple runs don't overwrite
    best_path = MODELS_DIR / (
        "best_model.pth" if arch == "efficientnet_b4"
        else f"best_model_{arch}.pth")
    best_f1 = 0.0

    def run_epoch(epoch_idx, phase, loader, optimizer=None):
        is_train = optimizer is not None
        model.train() if is_train else model.eval()
        losses, correct, n = [], 0, 0
        for x, y in tqdm(loader, desc=f"E{epoch_idx} {phase}",
                         leave=False):
            x, y = x.to(device), y.to(device)
            if is_train:
                optimizer.zero_grad()
            with torch.set_grad_enabled(is_train):
                logits = model(x)
                loss = criterion(logits, y)
                if is_train:
                    loss.backward()
                    optimizer.step()
            losses.append(loss.item())
            correct += (logits.argmax(1) == y).sum().item()
            n += y.size(0)
        return float(np.mean(losses)), correct / n

    # Stage 1 — frozen backbone, only train classifier head.
    # Multi-arch aware: get_feature_layers() returns the parameter list
    # of the backbone for the chosen architecture.
    backbone_params = get_feature_layers(model, arch)
    for p in backbone_params:
        p.requires_grad = False
    optim_s1 = optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr_s1)

    for epoch in range(1, epochs_s1 + 1):
        tr_loss, tr_acc = run_epoch(epoch, "S1-train",
                                    train_loader, optim_s1)
        val_metrics = evaluate(model, val_loader, device, class_names)
        history["epoch"].append(epoch)
        history["phase"].append("s1")
        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(val_metrics["accuracy"])
        history["val_f1"].append(val_metrics["f1_macro"])
        print(f"  E{epoch:02d} S1  loss {tr_loss:.4f}  "
              f"tr_acc {tr_acc:.3f}  val_acc {val_metrics['accuracy']:.3f}  "
              f"val_F1 {val_metrics['f1_macro']:.4f}")
        if val_metrics["f1_macro"] > best_f1:
            best_f1 = val_metrics["f1_macro"]
            torch.save({
                "model_state_dict": model.state_dict(),
                "val_f1": best_f1,
                "epoch": epoch, "phase": "s1",
                "class_order": class_names,
            }, best_path)

    # Stage 2 — unfreeze last N layers, lower LR, full fine-tune.
    # Multi-arch aware: use get_feature_layers() to find the right
    # parameter list for each backbone.
    print("\n  → Stage 2: unfreezing last 20 backbone layers, "
          f"lr={lr_s2:.0e} ({arch})")
    feat_layers = get_feature_layers(model, arch)
    for p in feat_layers[-20:]:
        p.requires_grad = True
    optim_s2 = optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=lr_s2)
    sched = optim.lr_scheduler.CosineAnnealingLR(optim_s2, T_max=epochs_s2)

    for epoch in range(1, epochs_s2 + 1):
        tr_loss, tr_acc = run_epoch(epochs_s1 + epoch, "S2-train",
                                    train_loader, optim_s2)
        sched.step()
        val_metrics = evaluate(model, val_loader, device, class_names)
        history["epoch"].append(epochs_s1 + epoch)
        history["phase"].append("s2")
        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(val_metrics["accuracy"])
        history["val_f1"].append(val_metrics["f1_macro"])
        print(f"  E{epochs_s1 + epoch:02d} S2  loss {tr_loss:.4f}  "
              f"tr_acc {tr_acc:.3f}  val_acc {val_metrics['accuracy']:.3f}  "
              f"val_F1 {val_metrics['f1_macro']:.4f}")
        if val_metrics["f1_macro"] > best_f1:
            best_f1 = val_metrics["f1_macro"]
            torch.save({
                "model_state_dict": model.state_dict(),
                "val_f1": best_f1,
                "epoch": epochs_s1 + epoch, "phase": "s2",
                "class_order": class_names,
            }, best_path)

    pd.DataFrame(history).to_csv(
        RESULTS_DIR / "training_history.csv", index=False)

    # Final test evaluation with the best checkpoint.
    print("\n=== STAGE 3 — Final test evaluation ===")
    ckpt = torch.load(best_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    test_metrics = evaluate(model, test_loader, device, class_names)

    print(f"\n  Test accuracy : {test_metrics['accuracy']:.4f}")
    print(f"  Test F1-macro : {test_metrics['f1_macro']:.4f}")
    print(f"  Test F1-weighted: {test_metrics['f1_weighted']:.4f}")
    print(f"  Best val F1   : {best_f1:.4f}\n")

    # Persist results in the same shape the GUI consumes.
    per_species = {}
    for sp_key, common in SPECIES_LABELS.items():
        block = test_metrics["report"].get(sp_key, {})
        if block:
            per_species[common] = {
                "precision": round(block["precision"], 4),
                "recall":    round(block["recall"], 4),
                "f1":        round(block["f1-score"], 4),
                "support":   int(block["support"]),
            }
    # Architecture-aware report. For the default (efficientnet_b4) the
    # file is reporte_final.json — overwrites the GUI-served metrics.
    # For other architectures, name it reporte_final_<arch>.json so
    # the 4-architecture comparison run produces 4 separate reports.
    arch_label = {
        "efficientnet_b4":    "EfficientNetB4",
        "resnet50":           "ResNet-50",
        "mobilenet_v3_large": "MobileNetV3-Large",
        "convnext_tiny":      "ConvNeXt-Tiny",
    }.get(arch, arch)
    report_filename = (
        "reporte_final.json" if arch == "efficientnet_b4"
        else f"reporte_final_{arch}.json")

    json.dump({
        "modelo": arch_label,
        "arch_key": arch,
        "dataset": "iNaturalist + ALA (post-expansion)",
        "total_test_images": sum(b["support"] for b in per_species.values()),
        "metricas_globales": {
            "accuracy":    round(test_metrics["accuracy"], 4),
            "f1_macro":    round(test_metrics["f1_macro"], 4),
            "f1_weighted": round(test_metrics["f1_weighted"], 4),
        },
        "objetivos": {
            "accuracy_80": test_metrics["accuracy"] >= 0.80,
            "f1_macro_85": test_metrics["f1_macro"] >= 0.85,
        },
        "por_especie": per_species,
        "training_config": {
            "arch": arch,
            "epochs_s1": epochs_s1, "epochs_s2": epochs_s2,
            "batch_size": batch_size,
            "lr_s1": lr_s1, "lr_s2": lr_s2, "seed": SEED,
        },
    }, open(RESULTS_DIR / report_filename, "w"), indent=2)

    pd.DataFrame(test_metrics["report"]).T.to_csv(
        RESULTS_DIR / "test_report.csv")

    # Plots — confusion matrix, learning curves, per-class F1.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        cm = confusion_matrix(test_metrics["y_true"], test_metrics["y_pred"])
        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(len(class_names)))
        ax.set_yticks(range(len(class_names)))
        labels = [SPECIES_LABELS.get(c, c) for c in class_names]
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)
        for i in range(len(class_names)):
            for j in range(len(class_names)):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black",
                        fontsize=10)
        ax.set_title(f"Confusion Matrix — F1-macro {test_metrics['f1_macro']:.3f}")
        ax.set_xlabel("Predicted"); ax.set_ylabel("True")
        fig.colorbar(im); fig.tight_layout()
        fig.savefig(RESULTS_DIR / "confusion_matrix.png", dpi=130)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 5))
        epochs = history["epoch"]
        ax.plot(epochs, history["train_acc"], label="Train acc", marker="o")
        ax.plot(epochs, history["val_acc"],   label="Val acc",   marker="s")
        ax.plot(epochs, history["val_f1"],    label="Val F1",    marker="^")
        ax.axvline(epochs_s1 + 0.5, color="grey", ls="--", alpha=0.6)
        ax.set_xlabel("Epoch"); ax.set_ylabel("Score"); ax.set_ylim(0, 1)
        ax.set_title("Learning curves (Stage 1 → Stage 2)")
        ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "learning_curves.png", dpi=130)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 5))
        names = list(per_species.keys())
        f1s   = [per_species[n]["f1"] for n in names]
        bars  = ax.barh(names, f1s)
        for b, v in zip(bars, f1s):
            ax.text(v + 0.01, b.get_y() + b.get_height() / 2,
                    f"{v:.2f}", va="center")
        ax.set_xlim(0, 1); ax.set_xlabel("F1-score")
        ax.set_title("F1 per species — test set")
        ax.grid(axis="x", alpha=0.3); fig.tight_layout()
        fig.savefig(RESULTS_DIR / "f1_por_especie.png", dpi=130)
        plt.close(fig)
    except Exception as e:
        print(f"  (plots failed: {e})")

    print(f"\n✅ Done. Outputs in:\n   {MODELS_DIR}/best_model.pth"
          f"\n   {RESULTS_DIR}/")


# ─── CLI ────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--skip-preprocess", action="store_true",
                   help="Skip dataset re-split; use existing dataset/processed/")
    p.add_argument("--arch", default="efficientnet_b4",
                   choices=["efficientnet_b4", "resnet50",
                            "mobilenet_v3_large", "convnext_tiny"],
                   help="Backbone to train (default: efficientnet_b4). "
                        "Run all four for the thesis comparison.")
    p.add_argument("--epochs-stage1", type=int, default=10)
    p.add_argument("--epochs-stage2", type=int, default=20)
    p.add_argument("--batch-size",    type=int, default=8,
                   help="Reduce if GPU runs out of VRAM (e.g. 4)")
    p.add_argument("--lr-stage1",     type=float, default=1e-3)
    p.add_argument("--lr-stage2",     type=float, default=1e-4)
    return p.parse_args()


def main():
    args = parse_args()
    set_seed()
    started = time.time()
    if not args.skip_preprocess:
        preprocess_dataset()
    else:
        print("⊘ Skipping preprocessing (--skip-preprocess set).")
    train(args.epochs_stage1, args.epochs_stage2, args.batch_size,
          args.lr_stage1, args.lr_stage2, arch=args.arch)
    mins = (time.time() - started) / 60
    print(f"\n⏱  Total wall time: {mins:.1f} min")


if __name__ == "__main__":
    main()
