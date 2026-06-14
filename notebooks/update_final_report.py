"""
Update results/reporte_final.json from results/test_predictions.csv.

This keeps the headline report synchronized with the current inference
pipeline, including YOLO adaptive policy and temperature scaling.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
)


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"
PREDICTIONS = RESULTS_DIR / "test_predictions.csv"
REPORT = RESULTS_DIR / "reporte_final.json"
CSV_REPORT = RESULTS_DIR / "test_report.csv"

CLASS_ORDER = [
    ("aquila_audax", "Wedge-tailed Eagle"),
    ("circus_assimilis", "Spotted Harrier"),
    ("elanus_axillaris", "Black-shouldered Kite"),
    ("falco_cenchroides", "Nankeen Kestrel"),
    ("falco_peregrinus", "Peregrine Falcon"),
    ("hieraaetus_morphnoides", "Little Eagle"),
    ("lophoictinia_isura", "Square-tailed Kite"),
    ("tachyspiza_fasciata", "Brown Goshawk"),
]


def main() -> None:
    rows = list(csv.DictReader(PREDICTIONS.open(encoding="utf-8", newline="")))
    y_true = [row["y_true"] for row in rows]
    y_pred = [row["y_pred"] for row in rows]
    labels = [key for key, _ in CLASS_ORDER]
    common = {key: name for key, name in CLASS_ORDER}

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    _, _, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    _, _, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    per_species = {}
    for idx, label in enumerate(labels):
        per_species[common[label]] = {
            "precision": round(float(precision[idx]), 4),
            "recall": round(float(recall[idx]), 4),
            "f1": round(float(f1[idx]), 4),
            "support": int(support[idx]),
        }

    report = {
        "modelo": "EfficientNetB4 + YOLO adaptive policy",
        "dataset": "iNaturalist + ALA (v1.5 processed split)",
        "total_test_images": len(rows),
        "metricas_globales": {
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
        },
        "objetivos": {
            "accuracy_80": float(accuracy_score(y_true, y_pred)) >= 0.80,
            "f1_macro_85": float(f1_macro) >= 0.85,
        },
        "por_especie": per_species,
        "prediction_distribution": dict(sorted(Counter(y_pred).items())),
        "training_config": {
            "epochs_s1": 10,
            "epochs_s2": 20,
            "batch_size": 8,
            "lr_s1": 0.001,
            "lr_s2": 0.0001,
            "seed": 42,
        },
        "inference_config": {
            "classifier": "EfficientNetB4",
            "detector": "YOLOv8n COCO bird class",
            "crop_policy": "adaptive",
            "temperature": 0.6934510469436646,
        },
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    report_rows = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    with CSV_REPORT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["", "precision", "recall", "f1-score", "support"])
        for label in labels:
            values = report_rows[label]
            writer.writerow([
                label,
                values["precision"],
                values["recall"],
                values["f1-score"],
                values["support"],
            ])
        acc = float(report_rows["accuracy"])
        writer.writerow(["accuracy", acc, acc, acc, acc])
        for label in ("macro avg", "weighted avg"):
            values = report_rows[label]
            writer.writerow([
                label,
                values["precision"],
                values["recall"],
                values["f1-score"],
                values["support"],
            ])

    print(json.dumps(report["metricas_globales"], indent=2))


if __name__ == "__main__":
    main()
