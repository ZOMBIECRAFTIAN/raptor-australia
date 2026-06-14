"""
Build a controlled demo set for presentations.

Selects:
- 5 high-confidence correct examples;
- 3 difficult examples from wrong or low-confidence predictions;
- 2 synthetic out-of-domain images.

Outputs:
- results/controlled_demo_set.csv
- docs/CONTROLLED_DEMO_SET.md
- demo/controlled/ood_gray.png
- demo/controlled/ood_sky_like.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"
DOCS_DIR = BASE_DIR / "docs"
DEMO_DIR = BASE_DIR / "demo" / "controlled"


def make_ood_images() -> list[dict]:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    gray = DEMO_DIR / "ood_gray.png"
    sky = DEMO_DIR / "ood_sky_like.png"

    Image.new("RGB", (380, 380), (180, 180, 180)).save(gray)
    img = Image.new("RGB", (380, 380), (130, 180, 220))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 260, 380, 380], fill=(80, 150, 90))
    draw.ellipse([40, 40, 160, 120], fill=(245, 245, 245))
    img.save(sky)

    return [
        {
            "category": "out_of_domain",
            "image_path": gray.relative_to(BASE_DIR).as_posix(),
            "expected_use": "Demonstrate closed-set weakness and out-of-domain feedback.",
            "y_true": "not_a_bird",
            "y_pred": "",
            "confidence": "",
        },
        {
            "category": "out_of_domain",
            "image_path": sky.relative_to(BASE_DIR).as_posix(),
            "expected_use": "Demonstrate that non-raptor scenes still require user caution.",
            "y_true": "not_a_raptor",
            "y_pred": "",
            "confidence": "",
        },
    ]


def main() -> None:
    pred_path = RESULTS_DIR / "test_predictions.csv"
    rows = list(csv.DictReader(pred_path.open(encoding="utf-8", newline="")))
    for row in rows:
        row["confidence_float"] = float(row["confidence"])
        row["top3_labels"] = [item["label"] for item in json.loads(row["top3"])]

    easy = [
        row for row in rows
        if row["y_true"] == row["y_pred"] and row["confidence_float"] >= 90
    ][:5]
    hard_wrong = [row for row in rows if row["y_true"] != row["y_pred"]]
    hard_low = [
        row for row in rows
        if row["y_true"] == row["y_pred"] and row["confidence_float"] < 60
    ]
    hard = (hard_wrong + hard_low)[:3]

    out_rows = []
    for row in easy:
        out_rows.append({
            "category": "easy_correct",
            "image_path": row["image_path"],
            "expected_use": "Show normal successful classification.",
            "y_true": row["y_true"],
            "y_pred": row["y_pred"],
            "confidence": row["confidence"],
        })
    for row in hard:
        out_rows.append({
            "category": "difficult",
            "image_path": row["image_path"],
            "expected_use": "Show uncertainty, top-3 alternatives, and error discussion.",
            "y_true": row["y_true"],
            "y_pred": row["y_pred"],
            "confidence": row["confidence"],
        })
    out_rows.extend(make_ood_images())

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / "controlled_demo_set.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["category", "image_path", "expected_use", "y_true", "y_pred", "confidence"],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    lines = [
        "# Controlled Demo Set",
        "",
        "Use this set for presentations so the demo is honest and repeatable.",
        "",
        "| Category | Image | Expected use | y_true | y_pred | confidence |",
        "|---|---|---|---|---|---:|",
    ]
    for row in out_rows:
        lines.append(
            f"| {row['category']} | `{row['image_path']}` | {row['expected_use']} | "
            f"`{row['y_true']}` | `{row['y_pred']}` | {row['confidence']} |"
        )
    lines.extend([
        "",
        "## Presentation Rule",
        "",
        "Show easy, difficult and out-of-domain cases. Do not present only successful examples.",
    ])
    (DOCS_DIR / "CONTROLLED_DEMO_SET.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
