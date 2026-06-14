"""
Grad-CAM Mosaic — 8 species in one figure
=========================================================
Produces a single 4x2 mosaic PNG showing the Grad-CAM heat-map
for one representative image of each of the 8 trained species.

This is the figure intended for Chapter 4 of the thesis
("Interpretabilidad — Grad-CAM"). Designed to be presentation
ready: each panel shows the bird with the heat-map overlaid,
labelled by the predicted species and top-1 confidence.

Methodologically based on Selvaraju et al., 2017
(https://arxiv.org/abs/1610.02391) and ports the pattern from
the author's prior project raptors-cnn (Veracruz, México).

Usage (from project root, with raptor_env active):
    python notebooks/gradcam_mosaic.py
    python notebooks/gradcam_mosaic.py
    python notebooks/gradcam_mosaic.py --out results/thesis_gradcam.png
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Reuse single-image script as a library — that file defines
# build_model(), get_target_layer(), get_eval_transform(),
# the GradCAM class and the canonical SPECIES_LABELS / paths.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gradcam import (
    build_model, get_target_layer, get_eval_transform,
    GradCAM, SPECIES_LABELS,
    BASE_DIR, MODEL_PATH, RESULTS_DIR, INPUT_SIZE,
)

DATASET_DIR = BASE_DIR / "dataset" / "raw"
SEED        = 42
SPECIES_KEYS = [
    "aquila_audax",
    "circus_assimilis",
    "elanus_axillaris",
    "falco_berigora",
    "falco_cenchroides",
    "falco_peregrinus",
    "haliaeetus_leucogaster",
    "haliastur_indus",
    "haliastur_sphenurus",
    "hieraaetus_morphnoides",
    "lophoictinia_isura",
    "milvus_migrans",
    "tachyspiza_fasciata",
    "tachyspiza_novaehollandiae",
]


def pick_representative_image(species_key: str) -> Path | None:
    """Pick a sharp, sufficiently-large image deterministically."""
    folder = DATASET_DIR / species_key
    if not folder.exists():
        return None
    candidates = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
    if not candidates:
        return None
    # Prefer the median-size image — neither tiniest nor biggest
    candidates.sort(key=lambda p: p.stat().st_size)
    return candidates[len(candidates) // 2]


def compute_cam(model: torch.nn.Module, image_path: Path,
                arch: str, device: torch.device,
                eval_tf) -> tuple[np.ndarray, int, np.ndarray]:
    img = Image.open(image_path).convert("RGB")
    x = eval_tf(img).unsqueeze(0).to(device)
    cam_engine = GradCAM(model, get_target_layer(model, arch))
    cam, pred_idx, probs = cam_engine(x)
    return cam, pred_idx, probs


def render_mosaic(panels: list[dict], out_path: Path,
                  arch_label: str) -> None:
    cols, rows = 4, 2
    fig, axes = plt.subplots(rows, cols, figsize=(20, 11),
                              dpi=130)
    fig.suptitle(
        f"Grad-CAM interpretability — Australian Raptor CNN "
        f"({arch_label})",
        fontsize=16, fontweight="bold", y=0.98)

    for ax, panel in zip(axes.flatten(), panels):
        if panel is None:
            ax.axis("off")
            continue

        img = Image.open(panel["image_path"]).convert("RGB").resize(
            (INPUT_SIZE, INPUT_SIZE))
        ax.imshow(img)
        ax.imshow(panel["cam"], cmap="jet", alpha=0.45)
        ax.axis("off")

        is_correct = panel["pred_label"] == panel["true_label"]
        marker     = "✓" if is_correct else "✗"
        color      = "#27AE60" if is_correct else "#C0392B"

        title = (
            f"{panel['true_label']}\n"
            f"{marker} pred: {panel['pred_label']} "
            f"({panel['confidence']:.1f}%)"
        )
        ax.set_title(title, fontsize=11, color=color,
                     pad=6, fontweight="medium")

    fig.text(
        0.5, 0.03,
        "Heat-map regions show where the CNN attended when "
        "producing each prediction. Concentration on wing, tail "
        "and body silhouettes validates morphological-feature "
        "learning (Selvaraju et al., 2017).",
        ha="center", fontsize=10, style="italic", color="#555")
    fig.tight_layout(rect=[0, 0.05, 1, 0.96])
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--arch", default="efficientnet_b4",
                   choices=["efficientnet_b4"])
    p.add_argument("--weights", default=str(MODEL_PATH))
    p.add_argument("--out", default=None,
                   help="Output PNG (default: results/gradcam_mosaic.png)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(SEED)

    arch_label = "EfficientNetB4"

    device = torch.device("cuda" if torch.cuda.is_available()
                          else "cpu")
    print(f"Grad-CAM mosaic — arch={args.arch} · device={device}")

    model = build_model(args.arch).to(device)
    ck = torch.load(args.weights, map_location=device, weights_only=True)
    if isinstance(ck, dict) and "model_state_dict" in ck:
        model.load_state_dict(ck["model_state_dict"])
    else:
        model.load_state_dict(ck)
    model.eval()

    eval_tf = get_eval_transform()

    # CLASS_ORDER inside Grad-CAM uses species_keys sorted alphabetically.
    # We need the mapping pred_idx → species label that matches the
    # *training* class order. SPECIES_LABELS in gradcam.py uses that
    # alphabetical order — see the module's top-level constant.
    panels: list[dict | None] = []
    for sp_key in SPECIES_KEYS:
        img_path = pick_representative_image(sp_key)
        if img_path is None:
            print(f"  ✗ {sp_key}: no image available — leaving panel blank")
            panels.append(None)
            continue
        print(f"  • {sp_key}: {img_path.name}")
        cam, pred_idx, probs = compute_cam(model, img_path,
                                            args.arch, device, eval_tf)
        # SPECIES_LABELS is alphabetical (same order as ImageFolder)
        # — see notebooks/gradcam.py
        true_label = {
            "aquila_audax":               "Wedge-tailed Eagle",
            "circus_assimilis":           "Spotted Harrier",
            "elanus_axillaris":           "Black-shouldered Kite",
            "falco_berigora":             "Brown Falcon",
            "falco_cenchroides":          "Nankeen Kestrel",
            "falco_peregrinus":           "Peregrine Falcon",
            "haliaeetus_leucogaster":     "White-bellied Sea-Eagle",
            "haliastur_indus":            "Brahminy Kite",
            "haliastur_sphenurus":        "Whistling Kite",
            "hieraaetus_morphnoides":     "Little Eagle",
            "lophoictinia_isura":         "Square-tailed Kite",
            "milvus_migrans":             "Black Kite",
            "tachyspiza_fasciata":        "Brown Goshawk",
            "tachyspiza_novaehollandiae": "Grey Goshawk",
        }[sp_key]

        panels.append({
            "image_path": img_path,
            "cam":        cam,
            "true_label": true_label,
            "pred_label": SPECIES_LABELS[pred_idx],
            "confidence": float(probs[pred_idx]) * 100.0,
        })

    out_path = Path(args.out) if args.out else (
        RESULTS_DIR / "gradcam_mosaic.png")
    render_mosaic(panels, out_path, arch_label)
    print(f"\n✓ Mosaic written to {out_path}")


if __name__ == "__main__":
    main()
