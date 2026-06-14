"""
Compare whole-image inference against YOLO-cropped inference.

The script uses the same EfficientNetB4 checkpoint and held-out test split.
It only runs the YOLO arm when local YOLO weights are available. This avoids
network downloads during reproducibility checks.

Outputs:
- results/yolo_crop_ablation.json
- results/yolo_crop_ablation.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[1]
GUI_DIR = BASE_DIR / "gui"
RESULTS_DIR = BASE_DIR / "results"
TEST_DIR = BASE_DIR / "dataset" / "processed" / "test"
MODEL_PATH = BASE_DIR / "models" / "best_model.pth"
YOLO_DEFAULT = BASE_DIR / "models" / "yolov8n.pt"
PREDICTIONS_PATH = RESULTS_DIR / "test_predictions.csv"


def iter_images(test_dir: Path):
    for sp_dir in sorted(p for p in test_dir.iterdir() if p.is_dir()):
        for img_path in sorted(sp_dir.iterdir()):
            if img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                yield sp_dir.name, img_path


def compute_metrics(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0, "accuracy": None, "mean_confidence": None}
    correct = np.array([row["y_true"] == row["y_pred"] for row in rows], dtype=float)
    conf = np.array([row["confidence"] for row in rows], dtype=float)
    return {
        "n": len(rows),
        "accuracy": float(correct.mean()),
        "mean_confidence": float(conf.mean()),
    }


def whole_image_metrics_from_predictions() -> dict:
    if not PREDICTIONS_PATH.exists():
        return {"n": 0, "accuracy": None, "mean_confidence": None}
    rows = []
    with PREDICTIONS_PATH.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "y_true": row["y_true"],
                "y_pred": row["y_pred"],
                "confidence": float(row["confidence"]),
            })
    return compute_metrics(rows)


def format_metric(value, digits: int = 4) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def write_report(report: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / "yolo_crop_ablation.json"
    out_md = RESULTS_DIR / "yolo_crop_ablation.md"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# YOLO-Crop vs Whole-Image Ablation",
        "",
        f"Status: **{report['status']}**",
        "",
        "| Mode | n | Accuracy | Mean confidence |",
        "|---|---:|---:|---:|",
    ]
    for mode in ("whole_image", "yolo_crop", "adaptive"):
        metrics = report["metrics"].get(mode, {})
        lines.append(
            f"| {mode} | {metrics.get('n', 0)} | "
            f"{format_metric(metrics.get('accuracy'))} | "
            f"{format_metric(metrics.get('mean_confidence'), 2)} |"
        )
    if report.get("note"):
        lines.extend(["", "## Note", "", report["note"]])
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", default=str(TEST_DIR))
    parser.add_argument("--yolo-weights", default=os.environ.get("RAPTOR_YOLO_WEIGHTS", str(YOLO_DEFAULT)))
    args = parser.parse_args()

    yolo_weights = Path(args.yolo_weights)
    if not yolo_weights.exists():
        write_report({
            "status": "skipped_missing_yolo_weights",
            "yolo_weights": str(yolo_weights),
            "metrics": {
                "whole_image": whole_image_metrics_from_predictions(),
                "yolo_crop": {"n": 0, "accuracy": None, "mean_confidence": None},
                "adaptive": whole_image_metrics_from_predictions(),
            },
            "note": (
                "Place YOLO weights at models/yolov8n.pt or set "
                "RAPTOR_YOLO_WEIGHTS, then rerun this script. The script does "
                "not trigger network downloads."
            ),
        })
        return

    sys.path.insert(0, str(GUI_DIR))
    from app import (
        CLASS_ORDER,
        AustralianRaptorCNN,
        YOLO_CROP_CONFIDENCE_GAIN,
        _select_yolo_crop,
        inference_transform,
        device,
    )

    model = AustralianRaptorCNN(num_classes=len(CLASS_ORDER)).to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    def predict_pil(img: Image.Image) -> tuple[str, float]:
        tensor = inference_transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1)[0].cpu().numpy()
        idx = int(np.argmax(probs))
        return CLASS_ORDER[idx], round(float(probs[idx]) * 100, 1)

    whole_rows = []
    crop_rows = []
    adaptive_rows = []
    detections = 0
    for y_true, img_path in iter_images(Path(args.test_dir)):
        img = Image.open(img_path).convert("RGB")
        pred, conf = predict_pil(img)
        whole_rows.append({"y_true": y_true, "y_pred": pred, "confidence": conf})

        crop, meta = _select_yolo_crop(img)
        if meta:
            detections += 1
        pred_crop, conf_crop = predict_pil(crop)
        crop_rows.append({
            "y_true": y_true,
            "y_pred": pred_crop,
            "confidence": conf_crop,
            "detected": bool(meta),
        })
        use_crop = bool(meta) and conf_crop >= conf + YOLO_CROP_CONFIDENCE_GAIN
        adaptive_rows.append({
            "y_true": y_true,
            "y_pred": pred_crop if use_crop else pred,
            "confidence": conf_crop if use_crop else conf,
        })

    report = {
        "status": "completed",
        "yolo_weights": str(yolo_weights),
        "n_yolo_detections": detections,
        "metrics": {
            "whole_image": compute_metrics(whole_rows),
            "yolo_crop": compute_metrics(crop_rows),
            "adaptive": compute_metrics(adaptive_rows),
        },
        "note": (
            "This is an inference ablation with the same EfficientNetB4 "
            "checkpoint. It does not retrain the classifier on cropped images."
        ),
    }
    write_report(report)


if __name__ == "__main__":
    main()
