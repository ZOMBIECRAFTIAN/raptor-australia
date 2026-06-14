"""
Temperature Scaling — Post-hoc Calibration
=========================================================
Implements the temperature-scaling correction of Guo et al.
(2017), "On calibration of modern neural networks" (ICML).
This is a single-parameter rescaling of the logits that
typically reduces Expected Calibration Error by 5-10× without
changing the top-1 predictions.

Method
------
- A scalar `T > 0` rescales the pre-softmax logits:
      p_calibrated = softmax(logits / T)
- T is fitted on the **validation set** (NOT the test set) by
  minimising NLL with L-BFGS over T.
- After fitting, evaluate ECE on the test set with the rescaled
  probabilities to obtain the calibrated ECE.

Why this matters
----------------
The web app shows the top-1 softmax probability as "confidence".
If the model is over-confident (typical of cross-entropy-trained
CNNs), users will trust wrong answers more than they should.
Temperature scaling is the cheapest fix in the literature and
should be applied before any production-style deployment.

Usage
-----
    python notebooks/temperature_scaling.py
    python notebooks/temperature_scaling.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE.parent
RESULTS_DIR = BASE_DIR / "results"

sys.path.insert(0, str(HERE))
from gradcam import build_model, get_eval_transform, MODEL_PATH


def _collect_logits(model: torch.nn.Module, device: torch.device,
                    split_dir: Path) -> tuple[torch.Tensor, torch.Tensor]:
    eval_tf = get_eval_transform()
    species = sorted([p for p in split_dir.iterdir() if p.is_dir()])
    name_to_idx = {p.name: i for i, p in enumerate(species)}

    logits_all, labels_all = [], []
    with torch.no_grad():
        for sp_dir in species:
            label = name_to_idx[sp_dir.name]
            for img_path in sorted(sp_dir.iterdir()):
                if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                    continue
                try:
                    img = Image.open(img_path).convert("RGB")
                except Exception:
                    continue
                x = eval_tf(img).unsqueeze(0).to(device)
                logits_all.append(model(x).cpu())
                labels_all.append(label)

    return (torch.cat(logits_all, dim=0),
            torch.tensor(labels_all, dtype=torch.long))


def fit_temperature(logits: torch.Tensor,
                    labels: torch.Tensor) -> float:
    """L-BFGS over the scalar temperature T."""
    T = torch.nn.Parameter(torch.ones(1) * 1.0)
    nll = torch.nn.CrossEntropyLoss()

    def _closure() -> torch.Tensor:
        opt.zero_grad()
        loss = nll(logits / T.clamp(min=1e-3), labels)
        loss.backward()
        return loss

    opt = torch.optim.LBFGS([T], lr=0.05, max_iter=200)
    opt.step(_closure)
    return float(T.detach().item())


def ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    preds = probs.argmax(axis=1)
    confidences = probs.max(axis=1)
    accuracies = (preds == labels).astype(float)
    edges = np.linspace(0, 1, n_bins + 1)
    out = 0.0
    n = len(probs)
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (confidences > lo) & (confidences <= hi)
        if sel.any():
            out += (sel.sum() / n) * abs(
                accuracies[sel].mean() - confidences[sel].mean()
            )
    return float(out)


def nll(probs: np.ndarray, labels: np.ndarray) -> float:
    """Negative log-likelihood from probabilities and integer labels."""
    eps = 1e-12
    selected = probs[np.arange(len(labels)), labels]
    return float(-np.log(np.clip(selected, eps, 1.0)).mean())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--arch", default="efficientnet_b4",
                   choices=["efficientnet_b4"])
    p.add_argument("--weights", default=str(MODEL_PATH))
    p.add_argument("--val-dir",  default=str(
        BASE_DIR / "dataset" / "processed" / "val"))
    p.add_argument("--test-dir", default=str(
        BASE_DIR / "dataset" / "processed" / "test"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    val_dir, test_dir = Path(args.val_dir), Path(args.test_dir)
    for d in (val_dir, test_dir):
        if not d.exists():
            sys.exit(f"ERROR: {d} not found. Run retrain.py preprocessing.")

    device = torch.device("cuda" if torch.cuda.is_available()
                          else "cpu")
    print(f"Temperature scaling — arch={args.arch} · device={device}")

    model = build_model(args.arch).to(device)
    ck = torch.load(args.weights, map_location=device, weights_only=True)
    if isinstance(ck, dict) and "model_state_dict" in ck:
        model.load_state_dict(ck["model_state_dict"])
    else:
        model.load_state_dict(ck)
    model.eval()

    print("Collecting validation logits...")
    val_logits, val_labels = _collect_logits(model, device, val_dir)
    print(f"  -> {len(val_logits)} examples")

    print("Fitting temperature with L-BFGS...")
    T = fit_temperature(val_logits, val_labels)
    print(f"  -> T = {T:.4f}")

    print("\nCollecting test logits...")
    test_logits, test_labels = _collect_logits(model, device, test_dir)
    print(f"  -> {len(test_logits)} examples")

    probs_raw       = F.softmax(test_logits,            dim=1).numpy()
    probs_calibrated = F.softmax(test_logits / max(T, 1e-3),
                                  dim=1).numpy()
    labels_np = test_labels.numpy()

    ece_before = ece(probs_raw,        labels_np)
    ece_after  = ece(probs_calibrated, labels_np)
    nll_before = nll(probs_raw, labels_np)
    nll_after  = nll(probs_calibrated, labels_np)

    acc_before = float((probs_raw.argmax(1) == labels_np).mean())
    acc_after  = float((probs_calibrated.argmax(1) == labels_np).mean())

    summary = {
        "arch":        args.arch,
        "temperature": T,
        "ece_before":  ece_before,
        "ece_after":   ece_after,
        "nll_before":  nll_before,
        "nll_after":   nll_after,
        "nll_delta":   nll_after - nll_before,
        "ece_reduction_factor": (ece_before / ece_after
                                  if ece_after > 0 else None),
        "accuracy_before": acc_before,
        "accuracy_after":  acc_after,
        "note": ("Temperature scaling preserves the top-1 argmax "
                 "by construction; any acc difference is numerical."),
    }
    print("\n" + json.dumps(summary, indent=2))

    out = RESULTS_DIR / f"temperature_scaling_{args.arch}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")

    if T > 1.05:
        print(f"\nInterpretation: T > 1 means the raw model was "
              f"over-confident. The web app should divide its "
              f"logits by T = {T:.3f} before softmax.")
    elif T < 0.95:
        print(f"\nInterpretation: T < 1 means the raw model was "
              f"under-confident. Apply the same T = {T:.3f} "
              f"rescaling for the deployed UI.")
    else:
        print("\nInterpretation: T ~= 1 -> the raw model is already "
              "reasonably calibrated; no rescaling needed.")


if __name__ == "__main__":
    main()
