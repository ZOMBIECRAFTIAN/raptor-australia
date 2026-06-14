"""
Compute top-3 utility metrics from results/test_predictions.csv.

Outputs:
- results/top3_utility.json
- results/top3_utility.md
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"


def parse_top3(value: str) -> list[dict]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", default=str(RESULTS_DIR / "test_predictions.csv"))
    args = parser.parse_args()

    path = Path(args.predictions)
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    if not rows:
        raise SystemExit(f"No rows in {path}")

    top1_correct = 0
    top3_correct = 0
    rescued = []
    per_species = defaultdict(lambda: {"n": 0, "top1": 0, "top3": 0})
    confusion_top1 = Counter()

    for row in rows:
        y_true = row["y_true"]
        y_pred = row["y_pred"]
        top3 = parse_top3(row.get("top3", "[]"))
        labels = [item.get("label") for item in top3]
        is_top1 = y_true == y_pred
        is_top3 = y_true in labels
        top1_correct += int(is_top1)
        top3_correct += int(is_top3)
        per_species[y_true]["n"] += 1
        per_species[y_true]["top1"] += int(is_top1)
        per_species[y_true]["top3"] += int(is_top3)
        if not is_top1:
            confusion_top1[(y_true, y_pred)] += 1
        if (not is_top1) and is_top3:
            rescued.append({
                "image_path": row["image_path"],
                "y_true": y_true,
                "y_pred": y_pred,
                "confidence": row["confidence"],
                "top3": top3,
            })

    n = len(rows)
    species_rows = {}
    for species, values in sorted(per_species.items()):
        species_rows[species] = {
            "n": values["n"],
            "top1_accuracy": values["top1"] / values["n"],
            "top3_accuracy": values["top3"] / values["n"],
        }

    report = {
        "n": n,
        "top1_accuracy": top1_correct / n,
        "top3_accuracy": top3_correct / n,
        "top3_gain": (top3_correct - top1_correct) / n,
        "top3_rescued_count": len(rescued),
        "top3_rescued_examples": rescued[:20],
        "per_species": species_rows,
        "most_common_top1_errors": [
            {"y_true": a, "y_pred": b, "n": count}
            for (a, b), count in confusion_top1.most_common(10)
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / "top3_utility.json"
    out_md = RESULTS_DIR / "top3_utility.md"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Top-3 Utility Analysis",
        "",
        f"Rows: **{n}**",
        f"Top-1 accuracy: **{report['top1_accuracy']:.4f}**",
        f"Top-3 accuracy: **{report['top3_accuracy']:.4f}**",
        f"Top-3 gain: **{report['top3_gain']:.4f}**",
        f"Top-3 rescued errors: **{report['top3_rescued_count']}**",
        "",
        "## Per-Species Utility",
        "",
        "| Species | n | Top-1 | Top-3 |",
        "|---|---:|---:|---:|",
    ]
    for species, values in species_rows.items():
        lines.append(
            f"| `{species}` | {values['n']} | {values['top1_accuracy']:.4f} | {values['top3_accuracy']:.4f} |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
