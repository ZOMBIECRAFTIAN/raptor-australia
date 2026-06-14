"""
Build a model registry entry for the v1.5 checkpoint.

Outputs:
- docs/MODEL_REGISTRY.md
- results/model_registry_v1_5.json
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "best_model.pth"
YOLO_MODEL_PATH = BASE_DIR / "models" / "yolov8n.pt"
RESULTS_DIR = BASE_DIR / "results"
DOCS_DIR = BASE_DIR / "docs"
REPORT_PATH = RESULTS_DIR / "reporte_final.json"


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    class_order = [
        "aquila_audax",
        "circus_assimilis",
        "elanus_axillaris",
        "falco_cenchroides",
        "falco_peregrinus",
        "hieraaetus_morphnoides",
        "lophoictinia_isura",
        "tachyspiza_fasciata",
    ]
    entry = {
        "model_id": "raptor-efficientnetb4-v1.5",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checkpoint": "models/best_model.pth",
        "checkpoint_sha256": sha256(MODEL_PATH),
        "architecture": "EfficientNetB4",
        "detector": "YOLOv8n COCO bird detector",
        "detector_weights": (
            "models/yolov8n.pt" if YOLO_MODEL_PATH.exists() else "yolov8n.pt"
        ),
        "detector_weights_sha256": sha256(YOLO_MODEL_PATH),
        "crop_policy": "adaptive",
        "calibration_temperature": 0.6934510469436646,
        "class_order": class_order,
        "dataset": {
            "processed_images": 1992,
            "train": 1590,
            "validation": 196,
            "test": report["total_test_images"],
            "sources": ["iNaturalist Australia", "Atlas of Living Australia"],
        },
        "metrics": report["metricas_globales"],
        "reproduction_commands": [
            "python notebooks/export_test_predictions.py",
            "python notebooks/update_final_report.py",
            "python notebooks/bootstrap_metrics.py --report-md",
            "python notebooks/error_analysis.py",
            "python notebooks/calibration_ece.py",
            "python notebooks/top3_utility.py",
            "python notebooks/yolo_crop_ablation.py",
            "python notebooks/run_tests.py",
            "python notebooks/healthcheck.py --verbose",
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "model_registry_v1_5.json").write_text(
        json.dumps(entry, indent=2), encoding="utf-8"
    )

    lines = [
        "# Model Registry",
        "",
        "## raptor-efficientnetb4-v1.5",
        "",
        f"- Checkpoint: `{entry['checkpoint']}`",
        f"- SHA-256: `{entry['checkpoint_sha256']}`",
        "- Architecture: EfficientNetB4",
        f"- Detector/cropper: {entry['detector']}",
        f"- Detector weights: `{entry['detector_weights']}`",
        f"- Detector SHA-256: `{entry['detector_weights_sha256']}`",
        f"- Crop policy: {entry['crop_policy']}",
        f"- Calibration temperature: {entry['calibration_temperature']}",
        "- Active classes: 8",
        f"- Test images: {entry['dataset']['test']}",
        f"- Accuracy: {entry['metrics']['accuracy']:.4f}",
        f"- Macro-F1: {entry['metrics']['f1_macro']:.4f}",
        f"- Weighted-F1: {entry['metrics']['f1_weighted']:.4f}",
        "",
        "## Class Order",
        "",
    ]
    lines.extend(f"{idx}. `{label}`" for idx, label in enumerate(class_order))
    lines.extend([
        "",
        "## Reproduction Commands",
        "",
        "```powershell",
        *entry["reproduction_commands"],
        "```",
    ])
    (DOCS_DIR / "MODEL_REGISTRY.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
