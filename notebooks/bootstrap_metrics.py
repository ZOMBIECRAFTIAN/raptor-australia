"""
Bootstrap Confidence Intervals for Classification Metrics
=========================================================
Computes 95 % CIs for top-1 accuracy, macro-F1, and per-class F1
via non-parametric bootstrap resampling on the held-out test set.

Required for MPhil-level reporting: a single point estimate of
accuracy is not enough — bootstrap CIs quantify how much of the
observed performance is signal vs sampling noise.

Methodology
-----------
- For B = 1000 bootstrap iterations, draw a same-size sample
  (with replacement) from the (y_true, y_pred) pairs and compute
  the metric.
- Report mean, 2.5 % and 97.5 % percentiles → 95 % CI.
- This is the percentile bootstrap (Efron, 1979; Hesterberg
  2015 for ML applications).

Usage
-----
    # After running retrain.py or export_test_predictions.py:
    python notebooks/bootstrap_metrics.py
    python notebooks/bootstrap_metrics.py --n-boot 5000
    python notebooks/bootstrap_metrics.py --report-md  # markdown out

Outputs
-------
- results/bootstrap_ci_efficientnet_b4.json  — machine-readable
- results/bootstrap_ci_efficientnet_b4.md    — paste-into-thesis markdown
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE.parent
RESULTS_DIR = BASE_DIR / "results"
SEED = 42


def percentile_ci(values: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """Two-sided alpha-level percentile CI."""
    lo = float(np.percentile(values, 100 * alpha / 2))
    hi = float(np.percentile(values, 100 * (1 - alpha / 2)))
    return lo, hi


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int) -> float:
    f1s = []
    for c in range(n_classes):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        denom = 2 * tp + fp + fn
        f1s.append((2 * tp / denom) if denom else 0.0)
    return float(np.mean(f1s))


def per_class_f1(y_true: np.ndarray, y_pred: np.ndarray,
                 n_classes: int) -> np.ndarray:
    out = np.zeros(n_classes)
    for c in range(n_classes):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        denom = 2 * tp + fp + fn
        out[c] = (2 * tp / denom) if denom else 0.0
    return out


def bootstrap(y_true: np.ndarray, y_pred: np.ndarray,
              n_classes: int, n_boot: int, rng: np.random.Generator
              ) -> dict:
    n = len(y_true)
    accs = np.zeros(n_boot)
    macs = np.zeros(n_boot)
    per_cls = np.zeros((n_boot, n_classes))
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt, yp = y_true[idx], y_pred[idx]
        accs[i] = float((yt == yp).mean())
        macs[i] = macro_f1(yt, yp, n_classes)
        per_cls[i] = per_class_f1(yt, yp, n_classes)

    return {
        "accuracy":    {
            "mean":  float(accs.mean()),
            "ci_lo": percentile_ci(accs)[0],
            "ci_hi": percentile_ci(accs)[1],
            "std":   float(accs.std()),
        },
        "macro_f1":   {
            "mean":  float(macs.mean()),
            "ci_lo": percentile_ci(macs)[0],
            "ci_hi": percentile_ci(macs)[1],
            "std":   float(macs.std()),
        },
        "per_class_f1": {
            "mean":  per_cls.mean(axis=0).tolist(),
            "ci_lo": np.percentile(per_cls,  2.5, axis=0).tolist(),
            "ci_hi": np.percentile(per_cls, 97.5, axis=0).tolist(),
        },
        "n_boot": n_boot,
        "n_test_images": int(n),
    }


def load_predictions(arch: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load (y_true, y_pred, class_names) from per-image predictions."""
    csv = RESULTS_DIR / f"test_predictions_{arch}.csv"
    if not csv.exists():
        csv = RESULTS_DIR / "test_predictions.csv"
    if not csv.exists():
        sys.exit(
            f"ERROR: cannot find {csv}. Run retrain.py or "
            "notebooks/export_test_predictions.py first."
        )

    import csv as _csv
    y_true, y_pred = [], []
    class_set: set[str] = set()
    with open(csv, encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            yt = row.get("y_true") or row.get("true_label")
            yp = row.get("y_pred") or row.get("predicted_label")
            if yt is None or yp is None:
                continue
            y_true.append(yt)
            y_pred.append(yp)
            class_set.add(yt)
            class_set.add(yp)

    class_names = sorted(class_set)
    name_to_idx = {n: i for i, n in enumerate(class_names)}
    yt_arr = np.array([name_to_idx[n] for n in y_true], dtype=np.int64)
    yp_arr = np.array([name_to_idx[n] for n in y_pred], dtype=np.int64)
    return yt_arr, yp_arr, class_names


def write_markdown(out_md: Path, arch: str, summary: dict,
                   class_names: list[str]) -> None:
    pc = summary["per_class_f1"]
    lines = [
        f"# Bootstrap 95 % CIs — {arch} (n_boot={summary['n_boot']})",
        "",
        f"Test-set size: **{summary['n_test_images']}** images.",
        "",
        "## Global metrics",
        "",
        "| Metric | Mean | 95 % CI |",
        "|---|---|---|",
        f"| Accuracy   | {summary['accuracy']['mean']:.4f} | "
        f"[{summary['accuracy']['ci_lo']:.4f}, "
        f"{summary['accuracy']['ci_hi']:.4f}] |",
        f"| Macro-F1   | {summary['macro_f1']['mean']:.4f} | "
        f"[{summary['macro_f1']['ci_lo']:.4f}, "
        f"{summary['macro_f1']['ci_hi']:.4f}] |",
        "",
        "## Per-class F1 (95 % CI)",
        "",
        "| Class | Mean F1 | 95 % CI |",
        "|---|---|---|",
    ]
    for i, name in enumerate(class_names):
        lines.append(
            f"| {name} | {pc['mean'][i]:.4f} | "
            f"[{pc['ci_lo'][i]:.4f}, {pc['ci_hi'][i]:.4f}] |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--arch", default="efficientnet_b4",
                   choices=["efficientnet_b4"],
                   help="Classifier architecture for output filenames")
    p.add_argument("--n-boot", type=int, default=1000,
                   help="Number of bootstrap iterations")
    p.add_argument("--report-md", action="store_true",
                   help="Also write a thesis-ready markdown summary")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(SEED)

    y_true, y_pred, class_names = load_predictions(args.arch)
    print(f"Loaded {len(y_true)} test predictions, "
          f"{len(class_names)} classes")

    print(f"Running bootstrap (B = {args.n_boot})…")
    summary = bootstrap(y_true, y_pred, len(class_names),
                        args.n_boot, rng)

    print(f"\nAccuracy: {summary['accuracy']['mean']:.4f} "
          f"[{summary['accuracy']['ci_lo']:.4f}, "
          f"{summary['accuracy']['ci_hi']:.4f}]")
    print(f"Macro-F1: {summary['macro_f1']['mean']:.4f} "
          f"[{summary['macro_f1']['ci_lo']:.4f}, "
          f"{summary['macro_f1']['ci_hi']:.4f}]")

    out_json = RESULTS_DIR / f"bootstrap_ci_{args.arch}.json"
    out_json.write_text(json.dumps(
        {**summary, "class_names": class_names, "arch": args.arch},
        indent=2,
    ), encoding="utf-8")
    print(f"\nWrote {out_json}")

    if args.report_md:
        out_md = RESULTS_DIR / f"bootstrap_ci_{args.arch}.md"
        write_markdown(out_md, args.arch, summary, class_names)
        print(f"Wrote {out_md}  (paste-ready for thesis)")


if __name__ == "__main__":
    main()
