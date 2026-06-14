"""
Probability Calibration — Expected Calibration Error (ECE)
=========================================================
Computes ECE from results/test_predictions.csv.

The web app shows the top-1 softmax probability as "confidence".
This script checks whether those confidences are calibrated by
binning predictions and comparing average confidence vs accuracy.

Usage
-----
    python notebooks/calibration_ece.py
    python notebooks/calibration_ece.py --n-bins 15

Outputs
-------
- results/calibration_efficientnet_b4.json
- results/reliability_diagram_efficientnet_b4.png
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
BASE_DIR = HERE.parent
RESULTS_DIR = BASE_DIR / "results"
PRIMARY_ARCH = "efficientnet_b4"


def load_prediction_confidences(path: Path) -> tuple[np.ndarray, np.ndarray]:
    if not path.exists():
        sys.exit(
            f"ERROR: cannot find {path}. Run retrain.py or "
            "notebooks/export_test_predictions.py first."
        )

    confidences = []
    correct = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                conf = float(row["confidence"]) / 100.0
            except Exception:
                continue
            confidences.append(conf)
            correct.append(1.0 if row.get("y_true") == row.get("y_pred") else 0.0)

    if not confidences:
        sys.exit(f"ERROR: no usable rows in {path}")

    return np.array(confidences), np.array(correct)


def expected_calibration_error(confidences: np.ndarray,
                               correct: np.ndarray,
                               n_bins: int = 10) -> tuple[float, dict]:
    """ECE with equal-width confidence bins."""
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    bins = []
    n = len(confidences)
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        in_bin = (confidences > lo) & (confidences <= hi)
        prop = in_bin.mean()
        if prop > 0:
            acc_bin = float(correct[in_bin].mean())
            conf_bin = float(confidences[in_bin].mean())
            ece += prop * abs(acc_bin - conf_bin)
        else:
            acc_bin, conf_bin = 0.0, 0.0
        bins.append({
            "lo": float(lo),
            "hi": float(hi),
            "n": int(in_bin.sum()),
            "accuracy": acc_bin,
            "confidence": conf_bin,
        })
    return float(ece), {"bins": bins, "n_total": int(n)}


def plot_reliability(ece: float, info: dict, out_path: Path) -> None:
    bins = info["bins"]
    confidences = [b["confidence"] for b in bins]
    accuracies = [b["accuracy"] for b in bins]
    widths = [b["hi"] - b["lo"] for b in bins]
    centers = [(b["lo"] + b["hi"]) / 2 for b in bins]

    fig, ax = plt.subplots(figsize=(6, 6), dpi=130)
    ax.bar(centers, accuracies, width=widths, edgecolor="white",
           color="#3498DB", alpha=0.85, label="Accuracy")
    ax.plot([0, 1], [0, 1], "--", color="#444", linewidth=1.5,
            label="Perfect calibration")
    ax.scatter(confidences, accuracies, color="#C0392B",
               zorder=5, s=30, label="Bin mean confidence")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Reliability diagram — EfficientNetB4 (ECE={ece:.4f})",
                 fontweight="bold")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--arch", default=PRIMARY_ARCH, choices=[PRIMARY_ARCH])
    p.add_argument("--n-bins", type=int, default=10)
    p.add_argument("--predictions", default=str(
        RESULTS_DIR / "test_predictions.csv"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.predictions)
    confidences, correct = load_prediction_confidences(path)
    ece, info = expected_calibration_error(
        confidences, correct, n_bins=args.n_bins)

    summary = {
        "arch": args.arch,
        "ece": ece,
        "n_bins": args.n_bins,
        "accuracy_from_predictions": float(correct.mean()),
        **info,
    }

    out_json = RESULTS_DIR / f"calibration_{args.arch}.json"
    out_json.write_text(json.dumps(summary, indent=2),
                        encoding="utf-8")
    out_png = RESULTS_DIR / f"reliability_diagram_{args.arch}.png"
    plot_reliability(ece, info, out_png)

    print(f"Expected Calibration Error: {ece:.4f}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_png}")


if __name__ == "__main__":
    main()
