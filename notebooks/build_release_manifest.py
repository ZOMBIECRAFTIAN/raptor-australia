"""
Build the v1.5 academic release manifest with SHA-256 checksums.

The manifest makes the release easier to audit: reviewers can see which
source files, documents and result artefacts belong to the academic baseline.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = PROJECT_ROOT / "results" / "release_manifest_v1_5.json"
MD_OUT = PROJECT_ROOT / "RELEASE_MANIFEST_v1_5.md"

RELEASE_FILES = [
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CITATION.cff",
    "CONTRIBUTING.md",
    ".gitignore",
    "requirements.txt",
    "requirements-lock.txt",
    "environment.yml",
    "Dockerfile",
    ".github/workflows/ci.yml",
    "gui/app.py",
    "gui/yolo_detector.py",
    "gui/species_data_i18n.py",
    "tests/test_project_integrity.py",
    "notebooks/healthcheck.py",
    "notebooks/run_tests.py",
    "notebooks/retrain.py",
    "notebooks/export_test_predictions.py",
    "notebooks/update_final_report.py",
    "notebooks/bootstrap_metrics.py",
    "notebooks/error_analysis.py",
    "notebooks/calibration_ece.py",
    "notebooks/build_thesis_docx.py",
    "notebooks/audit_thesis_docx.py",
    "notebooks/export_thesis_pdf.ps1",
    "notebooks/audit_thesis_pdf.py",
    "notebooks/audit_dataset_leakage.py",
    "notebooks/build_leakage_review_plan.py",
    "notebooks/yolo_crop_ablation.py",
    "notebooks/top3_utility.py",
    "notebooks/build_model_registry.py",
    "notebooks/build_controlled_demo_set.py",
    "docs/THESIS.md",
    "docs/SETUP.md",
    "docs/Australian_Raptor_Thesis_v1_5.docx",
    "docs/Australian_Raptor_Thesis_v1_5.pdf",
    "docs/DATASHEET.md",
    "docs/MODEL_CARD.md",
    "docs/METHODOLOGY.md",
    "docs/MASTERS_RESEARCH_PROPOSAL.md",
    "docs/SCIENTIFIC_DEFENSIBILITY.md",
    "docs/MASTERS_PRESENTATION_OUTLINE.md",
    "docs/ETHICS_DATA_GOVERNANCE.md",
    "docs/CLAIMS_MATRIX.md",
    "docs/SPLIT_GOVERNANCE.md",
    "docs/LEAKAGE_REVIEW_PROTOCOL.md",
    "docs/MODEL_REGISTRY.md",
    "docs/LIMITATIONS.md",
    "docs/CONTROLLED_DEMO_SET.md",
    "docs/DEFENSE_CHECKLIST.md",
    "docs/DEMO_SCRIPT.md",
    "docs/TAXONOMY_VERSIONING.md",
    "docs/SPECIES_ROADMAP.md",
    "results/reporte_final.json",
    "results/test_report.csv",
    "results/test_predictions.csv",
    "results/bootstrap_ci_efficientnet_b4.json",
    "results/bootstrap_ci_efficientnet_b4.md",
    "results/error_analysis_efficientnet_b4.json",
    "results/error_analysis_efficientnet_b4.md",
    "results/calibration_efficientnet_b4.json",
    "results/temperature_scaling_efficientnet_b4.json",
    "results/top3_utility.json",
    "results/top3_utility.md",
    "results/leakage_audit.json",
    "results/leakage_audit.md",
    "results/leakage_near_duplicate_pairs.jpg",
    "results/leakage_review_decisions.csv",
    "dataset/metadata/deleak_split_plan_v1_6.csv",
    "results/yolo_crop_ablation.json",
    "results/yolo_crop_ablation.md",
    "results/model_registry_v1_5.json",
    "results/controlled_demo_set.csv",
    "demo/controlled/ood_gray.png",
    "demo/controlled/ood_sky_like.png",
    "results/reliability_diagram_efficientnet_b4.png",
    "results/confusion_family_efficientnet_b4.png",
    "results/gradcam_mosaic.png",
    "results/thesis_docx_audit.json",
    "results/thesis_pdf_audit.json",
]

OPTIONAL_LARGE_FILES = [
    "models/best_model.pth",
    "models/yolov8n.pt",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    files = []
    missing = []
    for rel in RELEASE_FILES:
        path = PROJECT_ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        files.append({
            "path": rel.replace("\\", "/"),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "required": True,
        })
    optional_missing = []
    for rel in OPTIONAL_LARGE_FILES:
        path = PROJECT_ROOT / rel
        if not path.exists():
            optional_missing.append(rel)
            continue
        files.append({
            "path": rel.replace("\\", "/"),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "required": False,
        })

    manifest = {
        "release": "v1.5 academic baseline",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project": "Australian Raptor CNN + AUSLAN",
        "classifier": "EfficientNetB4",
        "detector": "YOLO",
        "active_species_count": 8,
        "files": files,
        "missing": missing,
        "optional_missing": optional_missing,
        "passed": not missing,
    }

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# Release Manifest - v1.5 Academic Baseline",
        "",
        f"Generated UTC: `{manifest['generated_at_utc']}`",
        "",
        "- Classifier: EfficientNetB4",
        "- Detector/cropper: YOLO",
        "- Active species: 8",
        "- Test predictions: `results/test_predictions.csv`",
        "",
        "## Verification Commands",
        "",
        "```powershell",
        "python notebooks\\run_tests.py",
        "python notebooks\\healthcheck.py --verbose",
        "python notebooks\\audit_thesis_docx.py",
        "python notebooks\\audit_thesis_pdf.py",
        "python notebooks\\build_release_manifest.py",
        "```",
        "",
        "## Files",
        "",
        "| Path | Size bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for item in files:
        label = item["path"]
        if not item.get("required", True):
            label = f"{label} (optional large artefact)"
        lines.append(
            f"| `{label}` | {item['size_bytes']} | `{item['sha256']}` |"
        )
    if missing:
        lines.extend(["", "## Missing Files", ""])
        for rel in missing:
            lines.append(f"- `{rel}`")
    if optional_missing:
        lines.extend(["", "## Optional Large Artefacts Not Present", ""])
        for rel in optional_missing:
            lines.append(f"- `{rel}`")

    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
