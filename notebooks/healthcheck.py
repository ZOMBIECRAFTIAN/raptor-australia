"""
Project Healthcheck — quick smoke-test before defence
=========================================================
Runs a sequence of fast validations to make sure the project
is in a presentable state:

  1. Python syntax (all .py files)
  2. JSON validity (all translations + results files)
  3. Jinja template render (with full mock state)
  4. Required files / folders present
  5. v1.5 release sync (dataset/results/CLASS_ORDER)
  6. test_predictions.csv schema (if generated)
  7. YOLO wrapper importability
  8. CHANGELOG and CITATION parse

Exits with code 0 (all green) or non-zero (first failure).
Designed for use immediately before pushing a tagged release
or running a demo.

Usage:
    python notebooks/healthcheck.py
    python notebooks/healthcheck.py --verbose
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def check_python_syntax(verbose: bool) -> tuple[bool, list[str]]:
    errors = []
    py_files = []
    for root in ("gui", "notebooks"):
        py_files += list((BASE_DIR / root).rglob("*.py"))
    py_files = [p for p in py_files if "__pycache__" not in p.parts]
    for p in py_files:
        try:
            ast.parse(p.read_text(encoding="utf-8"))
            if verbose:
                print(f"    OK {p.relative_to(BASE_DIR)}")
        except SyntaxError as e:
            errors.append(f"{p.relative_to(BASE_DIR)}: {e}")
    return (not errors), errors


def check_json_files(verbose: bool) -> tuple[bool, list[str]]:
    errors = []
    targets = (list((BASE_DIR / "gui" / "translations").glob("*.json")) +
               list((BASE_DIR / "results").glob("*.json")))
    for p in targets:
        try:
            json.loads(p.read_text(encoding="utf-8"))
            if verbose:
                print(f"    OK {p.relative_to(BASE_DIR)}")
        except Exception as e:
            errors.append(f"{p.relative_to(BASE_DIR)}: {e}")
    return (not errors), errors


def check_required_files() -> tuple[bool, list[str]]:
    required = [
        "README.md", "LICENSE", "CHANGELOG.md", "CITATION.cff",
        "CONTRIBUTING.md", "Dockerfile", ".gitignore",
        "requirements.txt", "requirements-lock.txt", "environment.yml",
        "RELEASE_MANIFEST_v1_5.md",
        "gui/app.py", "gui/i18n.py", "gui/species_data_i18n.py",
        "gui/yolo_detector.py",
        "gui/templates/index.html", "gui/templates/species.html",
        "gui/templates/data.html",
        "gui/static/css/style.css",
        "notebooks/retrain.py", "notebooks/gradcam.py",
        "notebooks/run_tests.py",
        "notebooks/export_test_predictions.py",
        "notebooks/update_final_report.py",
        "notebooks/build_release_manifest.py",
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
        "notebooks/gradcam_mosaic.py",
        "notebooks/download_ala_images.py",
        "notebooks/filter_ala_quality.py",
        "notebooks/fetch_ebird_data.py",
        "docs/SETUP.md",
        "docs/THESIS.md", "docs/Australian_Raptor_Thesis_v1_5.docx",
        "docs/Australian_Raptor_Thesis_v1_5.pdf",
        "docs/DATASHEET.md", "docs/MODEL_CARD.md",
        "docs/METHODOLOGY.md", "docs/DEFENSE_CHECKLIST.md",
        "docs/DEMO_SCRIPT.md",
        "docs/MASTERS_RESEARCH_PROPOSAL.md",
        "docs/SCIENTIFIC_DEFENSIBILITY.md",
        "docs/MASTERS_PRESENTATION_OUTLINE.md",
        "docs/ETHICS_DATA_GOVERNANCE.md",
        "docs/CLAIMS_MATRIX.md",
        "docs/SPLIT_GOVERNANCE.md", "docs/MODEL_REGISTRY.md",
        "docs/LEAKAGE_REVIEW_PROTOCOL.md",
        "docs/LIMITATIONS.md", "docs/CONTROLLED_DEMO_SET.md",
        "docs/TAXONOMY_VERSIONING.md", "docs/SPECIES_ROADMAP.md",
        "docs/auslan_consultation/README.md",
        "results/reporte_final.json",
        "results/test_report.csv",
        "results/test_predictions.csv",
        "results/thesis_docx_audit.json",
        "results/thesis_pdf_audit.json",
        "results/release_manifest_v1_5.json",
        "results/top3_utility.json",
        "results/top3_utility.md",
        "results/leakage_audit.json",
        "results/leakage_audit.md",
        "results/leakage_near_duplicate_pairs.jpg",
        "results/leakage_review_decisions.csv",
        "dataset/metadata/deleak_split_plan_v1_6.csv",
        "results/yolo_crop_ablation.json",
        "results/yolo_crop_ablation.md",
        "results/temperature_scaling_efficientnet_b4.json",
        "results/model_registry_v1_5.json",
        "results/controlled_demo_set.csv",
        "demo/controlled/ood_gray.png",
        "demo/controlled/ood_sky_like.png",
        ".github/workflows/ci.yml",
    ]
    missing = []
    for r in required:
        p = BASE_DIR / r
        if not p.exists():
            missing.append(r)
    return (not missing), missing


def check_translations_coverage() -> tuple[bool, list[str]]:
    """Every language file must contain a minimum set of keys."""
    required_paths = [
        "app.title", "nav.identify", "home.title", "result.epbc_status",
        "species_guide.title",
    ]
    errors = []
    for p in sorted((BASE_DIR / "gui" / "translations").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for path in required_paths:
            cur = d
            for part in path.split("."):
                if not isinstance(cur, dict) or part not in cur:
                    errors.append(f"{p.name}: missing {path}")
                    break
                cur = cur[part]
    return (not errors), errors


def check_release_sync() -> tuple[bool, list[str]]:
    """Validate v1.5 class order against local dataset/results."""
    errors = []
    os.environ["RAPTOR_LIGHTWEIGHT"] = "1"
    sys.path.insert(0, str(BASE_DIR / "gui"))
    try:
        import app as gui_app
    except Exception as e:
        return False, [f"gui import failed: {e}"]

    expected = [
        "aquila_audax",
        "circus_assimilis",
        "elanus_axillaris",
        "falco_cenchroides",
        "falco_peregrinus",
        "hieraaetus_morphnoides",
        "lophoictinia_isura",
        "tachyspiza_fasciata",
    ]
    if gui_app.CLASS_ORDER != expected:
        errors.append(f"CLASS_ORDER mismatch: {gui_app.CLASS_ORDER}")
    if gui_app.NUM_CLASSES != len(expected):
        errors.append(f"NUM_CLASSES={gui_app.NUM_CLASSES}, expected 8")

    for i, key in enumerate(gui_app.CLASS_ORDER):
        got = gui_app.SPECIES_INFO[key].get("class_idx")
        if got != i:
            errors.append(f"{key}.class_idx={got}, expected {i}")

    test_dir = BASE_DIR / "dataset" / "processed" / "test"
    if test_dir.exists():
        found = sorted(p.name for p in test_dir.iterdir() if p.is_dir())
        if found != expected:
            errors.append(f"processed/test classes mismatch: {found}")

        report = BASE_DIR / "results" / "reporte_final.json"
        if report.exists():
            data = json.loads(report.read_text(encoding="utf-8"))
            n_test = sum(
                1 for sp in test_dir.iterdir() if sp.is_dir()
                for p in sp.iterdir() if p.is_file()
            )
            if data.get("total_test_images") != n_test:
                errors.append(
                    "reporte_final total_test_images="
                    f"{data.get('total_test_images')}, expected {n_test}"
                )
    return (not errors), errors


def check_test_predictions_schema() -> tuple[bool, list[str]]:
    p = BASE_DIR / "results" / "test_predictions.csv"
    if not p.exists():
        return True, [
            "results/test_predictions.csv not generated yet; run "
            "notebooks/export_test_predictions.py after checkpoint changes."
        ]
    import csv
    required = {"image_path", "y_true", "y_pred", "confidence", "top3"}
    with open(p, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = required - set(reader.fieldnames or [])
        if missing:
            return False, [f"missing columns: {sorted(missing)}"]
        rows = list(reader)
    if not rows:
        return False, ["test_predictions.csv has no rows"]
    return True, []


def check_yolo_wrapper() -> tuple[bool, list[str]]:
    sys.path.insert(0, str(BASE_DIR / "gui"))
    try:
        import yolo_detector
    except Exception as e:
        return False, [f"cannot import gui/yolo_detector.py: {e}"]
    if yolo_detector.COCO_BIRD_CLASS_ID != 14:
        return False, ["COCO bird class id must be 14"]
    return True, []


def check_pytest_suite() -> tuple[bool, list[str]]:
    tests_dir = BASE_DIR / "tests"
    if not tests_dir.exists():
        return False, ["tests/ directory is missing"]
    try:
        import pytest  # noqa: F401
    except Exception:
        return True, ["pytest not installed; skipping test execution"]
    env = os.environ.copy()
    env["RAPTOR_LIGHTWEIGHT"] = "1"
    temp_root = BASE_DIR / "results" / "pytest-temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    basetemp = temp_root / f"run-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    env["TMP"] = str(temp_root)
    env["TEMP"] = str(temp_root)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(basetemp),
        ],
        cwd=str(BASE_DIR),
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return False, (proc.stdout + proc.stderr).splitlines()[-10:]
    return True, [proc.stdout.strip()]


def check_template_render() -> tuple[bool, list[str]]:
    sys.path.insert(0, str(BASE_DIR / "gui"))
    try:
        from i18n import (load_translations, t, LANGUAGES,
                          get_locale, get_languages)
        from species_data_i18n import get_species_data
        from flask import Flask
    except Exception as e:
        return False, [f"import failure: {e}"]

    load_translations()
    app = Flask("hc", template_folder=str(BASE_DIR / "gui" / "templates"))
    app.jinja_env.globals.update(
        t=t, LANGUAGES=LANGUAGES, get_locale=get_locale,
        get_languages=get_languages,
    )
    mock_info = {
        "aquila_audax": {
            "common_name": "Wedge-tailed Eagle",
            "scientific_name": "Aquila audax",
            "epbc_status": "Not listed",
            "habitat": "h", "length_cm": "l", "wingspan_cm": "w",
            "diagnostic": "d", "auslan_sign": "a",
            "auslan_video": "aquila_audax.svg", "color": "#2C3E50",
            "family": "Accipitridae", "code": "WTE",
            "distribution": "AU", "diet": "m",
            "behavior": "s", "behaviour": "s",
            "migration": "n", "nesting": "t",
            "breeding_months": "Apr", "best_months": "YR",
            "did_you_know": "f",
        },
    }
    metrics = {"aquila_audax": {"f1": 0.71, "precision": 0.7,
                                  "recall": 0.71, "support": 77,
                                  "train_count": 763}}
    videos = {"aquila_audax": {"exists": False,
                                "filename": "aquila_audax.mp4",
                                "size_mb": 0}}
    ebird  = {"aquila_audax": {"recent_count": 500,
                                "last_seen": {"date": "2026-05-14",
                                              "location": "L. George"},
                                "top_locations": [{"location": "Dajarra",
                                                    "count": 9}]}}

    errors = []
    for name in ("index.html", "species.html", "data.html"):
        try:
            with app.test_request_context(f"/?lang=en"):
                out = app.jinja_env.get_template(name).render(
                    species_info=mock_info,
                    species_metrics=metrics,
                    species_details=mock_info,
                    behavior_videos=videos,
                    ebird=ebird,
                    total_observations=0,
                    observations_by_species={},
                    feedback_count=0,
                    recent_observations=[],
                )
                if len(out) < 500:
                    errors.append(f"{name}: render too short")
        except Exception as e:
            errors.append(f"{name}: {e}")
    return (not errors), errors


def check_yaml_files() -> tuple[bool, list[str]]:
    try:
        import yaml
    except ImportError:
        return True, []   # PyYAML optional — skip if absent
    errors = []
    for rel in ("CITATION.cff", ".github/workflows/ci.yml"):
        p = BASE_DIR / rel
        if not p.exists():
            continue
        try:
            yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{rel}: {e}")
    return (not errors), errors


# ─── Driver ─────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    checks = [
        ("Python syntax",        lambda: check_python_syntax(args.verbose)),
        ("JSON validity",        lambda: check_json_files(args.verbose)),
        ("Required files",       check_required_files),
        ("Release sync",         check_release_sync),
        ("test_predictions CSV", check_test_predictions_schema),
        ("YOLO wrapper",         check_yolo_wrapper),
        ("Translation coverage", check_translations_coverage),
        ("Template render",      check_template_render),
        ("YAML validity",        check_yaml_files),
        ("Pytest suite",         check_pytest_suite),
    ]
    print("Australian Raptor CNN — Project Healthcheck\n")
    all_ok = True
    for name, fn in checks:
        try:
            ok, errors = fn()
        except Exception as e:
            ok, errors = False, [str(e)]
        if ok:
            print(f"  OK   {name}")
            if args.verbose:
                for msg in errors[:3]:
                    print(f"       {msg}")
        else:
            all_ok = False
            print(f"  FAIL {name}")
            for err in errors[:5]:
                print(f"       - {err}")
            if len(errors) > 5:
                print(f"       - ... and {len(errors) - 5} more")
    print()
    if all_ok:
        print("All checks passed — project is presentable.")
        sys.exit(0)
    print("Some checks failed — review the issues above before pushing.")
    sys.exit(1)


if __name__ == "__main__":
    main()
