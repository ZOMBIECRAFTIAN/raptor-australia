"""
Export per-image test predictions for thesis metrics.

This script evaluates the current Flask-served checkpoint on
dataset/processed/test and writes:

    results/test_predictions.csv

Columns:
    image_path,y_true,y_pred,confidence,top3

The CSV is the source for bootstrap CIs, calibration/ECE and
taxonomy-aware error analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
GUI_DIR = BASE_DIR / "gui"
RESULTS_DIR = BASE_DIR / "results"
TEST_DIR = BASE_DIR / "dataset" / "processed" / "test"


def iter_images(test_dir: Path):
    for sp_dir in sorted(p for p in test_dir.iterdir() if p.is_dir()):
        for img_path in sorted(sp_dir.iterdir()):
            if img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                yield sp_dir.name, img_path


def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--test-dir", default=str(TEST_DIR))
    p.add_argument("--out", default=str(RESULTS_DIR / "test_predictions.csv"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    test_dir = Path(args.test_dir)
    out_path = Path(args.out)
    if not test_dir.exists():
        sys.exit(f"ERROR: missing test directory: {test_dir}")

    sys.path.insert(0, str(GUI_DIR))
    from app import app, predict_image

    rows = []
    with app.test_request_context("/?lang=en"):
        for y_true, img_path in iter_images(test_dir):
            pred = predict_image(img_path)
            rows.append({
                "image_path": img_path.relative_to(BASE_DIR).as_posix(),
                "y_true": y_true,
                "y_pred": pred["species_key"],
                "confidence": pred["confidence"],
                "top3": json.dumps([
                    {
                        "label": item["species_key"],
                        "confidence": item["confidence"],
                    }
                    for item in pred["top3"]
                ], ensure_ascii=False),
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["image_path", "y_true", "y_pred",
                        "confidence", "top3"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} predictions to {out_path}")


if __name__ == "__main__":
    main()
