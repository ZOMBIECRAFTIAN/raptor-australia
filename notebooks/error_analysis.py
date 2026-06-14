"""
Taxonomy-aware Error Analysis
=========================================================
Produces three artefacts from per-image test predictions:

1. results/error_analysis_<arch>.json  — machine-readable
2. results/confusion_family_<arch>.png — 2×2 family confusion
3. results/error_analysis_<arch>.md    — markdown for thesis

Why family-grouped error analysis?
----------------------------------
A misclassification of one falcon as another falcon is far less
costly to a citizen scientist than mistaking a falcon for an
eagle. Reporting both fine-grained AND family-level confusion
gives the supervisor a calibrated view of model failure modes.

The bird taxonomy used here follows the IOC World Bird List
v14.1 (Gill, Donsker & Rasmussen 2024) — see
docs/TAXONOMY_VERSIONING.md.

Usage
-----
    python notebooks/error_analysis.py
    python notebooks/error_analysis.py
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

# ─── Taxonomy mapping ───────────────────────────────────
# Maps the v1.5 species keys to their family per IOC 14.1.
FAMILY: dict[str, str] = {
    "aquila_audax":             "Accipitridae",
    "circus_assimilis":         "Accipitridae",
    "elanus_axillaris":         "Accipitridae",
    "falco_cenchroides":        "Falconidae",
    "falco_peregrinus":         "Falconidae",
    "hieraaetus_morphnoides":   "Accipitridae",
    "lophoictinia_isura":       "Accipitridae",
    "tachyspiza_fasciata":      "Accipitridae",
}


def load_predictions(arch: str) -> tuple[list[str], list[str]]:
    """Return (y_true, y_pred) as parallel lists of species keys."""
    csv_path = RESULTS_DIR / f"test_predictions_{arch}.csv"
    if not csv_path.exists():
        csv_path = RESULTS_DIR / "test_predictions.csv"
    if not csv_path.exists():
        sys.exit(
            f"ERROR: cannot find {csv_path}. Run retrain.py or "
            "notebooks/export_test_predictions.py first."
        )

    y_true, y_pred = [], []
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yt = row.get("y_true") or row.get("true_label")
            yp = row.get("y_pred") or row.get("predicted_label")
            if yt and yp:
                y_true.append(yt)
                y_pred.append(yp)
    return y_true, y_pred


def family_confusion(y_true: list[str], y_pred: list[str]
                     ) -> tuple[np.ndarray, list[str]]:
    families = sorted({FAMILY[y] for y in y_true}
                       | {FAMILY[y] for y in y_pred})
    idx = {f: i for i, f in enumerate(families)}
    M = np.zeros((len(families), len(families)), dtype=int)
    for yt, yp in zip(y_true, y_pred):
        M[idx[FAMILY[yt]], idx[FAMILY[yp]]] += 1
    return M, families


def plot_family_confusion(M: np.ndarray, families: list[str],
                          arch: str, out_path: Path) -> None:
    n = len(families)
    fig, ax = plt.subplots(figsize=(5.5, 5), dpi=130)
    im = ax.imshow(M, cmap="Blues", aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(families, rotation=15, ha="right")
    ax.set_yticklabels(families)
    ax.set_xlabel("Predicted family")
    ax.set_ylabel("True family")
    ax.set_title(f"Family-level confusion — {arch}", fontweight="bold")

    # Numeric annotations
    threshold = M.max() / 2.0
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{M[i, j]}",
                    ha="center", va="center",
                    color=("white" if M[i, j] > threshold else "#222"),
                    fontsize=12, fontweight="medium")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def summarise(y_true: list[str], y_pred: list[str]) -> dict:
    n_total = len(y_true)
    fine_correct  = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    fam_correct   = sum(1 for t, p in zip(y_true, y_pred)
                        if FAMILY[t] == FAMILY[p])

    cross_family = [(t, p) for t, p in zip(y_true, y_pred)
                    if FAMILY[t] != FAMILY[p]]

    # Top confusions (off-diagonal)
    pairs: dict[tuple[str, str], int] = {}
    for t, p in zip(y_true, y_pred):
        if t != p:
            pairs[(t, p)] = pairs.get((t, p), 0) + 1
    top_confusions = sorted(pairs.items(),
                            key=lambda kv: -kv[1])[:10]

    return {
        "n_test":               n_total,
        "fine_accuracy":        fine_correct / n_total,
        "family_accuracy":      fam_correct / n_total,
        "cross_family_errors":  len(cross_family),
        "cross_family_rate":    len(cross_family) / n_total,
        "top_confusions": [
            {"true": t, "pred": p, "n": n}
            for (t, p), n in top_confusions
        ],
    }


def write_markdown(out_md: Path, arch: str, summary: dict,
                   M: np.ndarray, families: list[str]) -> None:
    lines = [
        f"# Error analysis — {arch}",
        "",
        f"- Test set size: **{summary['n_test']}** images",
        f"- Fine-grained (8-class) accuracy: "
        f"**{summary['fine_accuracy']:.4f}**",
        f"- Family-level (2-class) accuracy:  "
        f"**{summary['family_accuracy']:.4f}**",
        f"- Cross-family errors: "
        f"**{summary['cross_family_errors']}** "
        f"({summary['cross_family_rate']*100:.1f}% of test set)",
        "",
        "## Family-level confusion",
        "",
        "| " + " | ".join(["true \\ pred"] + families) + " |",
        "|" + "---|" * (len(families) + 1),
    ]
    for i, fam in enumerate(families):
        row = [fam] + [str(M[i, j]) for j in range(len(families))]
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Top 10 confusions (off-diagonal)",
        "",
        "| Rank | True species | Predicted species | n | Family-crossing? |",
        "|---|---|---|---|---|",
    ]
    for k, c in enumerate(summary["top_confusions"], start=1):
        crossing = "yes" if FAMILY[c["true"]] != FAMILY[c["pred"]] else "same"
        lines.append(
            f"| {k} | {c['true']} | {c['pred']} | {c['n']} | {crossing} |"
        )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--arch", default="efficientnet_b4",
                   choices=["efficientnet_b4"])
    return p.parse_args()


def main() -> None:
    args = parse_args()
    y_true, y_pred = load_predictions(args.arch)

    print(f"Loaded {len(y_true)} predictions for {args.arch}")
    summary = summarise(y_true, y_pred)
    M, families = family_confusion(y_true, y_pred)

    out_json = RESULTS_DIR / f"error_analysis_{args.arch}.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    out_png = RESULTS_DIR / f"confusion_family_{args.arch}.png"
    plot_family_confusion(M, families, args.arch, out_png)

    out_md = RESULTS_DIR / f"error_analysis_{args.arch}.md"
    write_markdown(out_md, args.arch, summary, M, families)

    print(f"\nWrote {out_json}")
    print(f"Wrote {out_png}")
    print(f"Wrote {out_md}\n")
    print(f"Fine-grained accuracy: {summary['fine_accuracy']:.4f}")
    print(f"Family-level accuracy: {summary['family_accuracy']:.4f}")
    print(f"Cross-family errors:   {summary['cross_family_errors']} "
          f"({summary['cross_family_rate']*100:.1f}%)")


if __name__ == "__main__":
    main()
