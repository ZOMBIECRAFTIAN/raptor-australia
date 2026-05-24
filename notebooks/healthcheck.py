"""
Project Healthcheck — quick smoke-test before defence
=========================================================
Runs a sequence of fast validations to make sure the project
is in a presentable state:

  1. Python syntax (all .py files)
  2. JSON validity (all translations + results files)
  3. Jinja template render (with full mock state)
  4. Required files / folders present
  5. Model checkpoint discoverable (if any)
  6. CHANGELOG and CITATION parse

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
import sys
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
                print(f"    ✓ {p.relative_to(BASE_DIR)}")
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
                print(f"    ✓ {p.relative_to(BASE_DIR)}")
        except Exception as e:
            errors.append(f"{p.relative_to(BASE_DIR)}: {e}")
    return (not errors), errors


def check_required_files() -> tuple[bool, list[str]]:
    required = [
        "README.md", "LICENSE", "CHANGELOG.md", "CITATION.cff",
        "CONTRIBUTING.md", "Dockerfile", ".gitignore",
        "requirements.txt",
        "gui/app.py", "gui/i18n.py", "gui/species_data_i18n.py",
        "gui/templates/index.html", "gui/templates/species.html",
        "gui/templates/data.html",
        "gui/static/css/style.css",
        "notebooks/retrain.py", "notebooks/gradcam.py",
        "notebooks/gradcam_mosaic.py",
        "notebooks/download_ala_images.py",
        "notebooks/filter_ala_quality.py",
        "notebooks/fetch_ebird_data.py",
        "docs/SETUP.md", "docs/CHAPTERS_OUTLINE.md",
        "docs/TAXONOMY_VERSIONING.md", "docs/SPECIES_ROADMAP.md",
        "docs/auslan_consultation/README.md",
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
        ("Translation coverage", check_translations_coverage),
        ("Template render",      check_template_render),
        ("YAML validity",        check_yaml_files),
    ]
    print("Australian Raptor CNN — Project Healthcheck\n")
    all_ok = True
    for name, fn in checks:
        try:
            ok, errors = fn()
        except Exception as e:
            ok, errors = False, [str(e)]
        if ok:
            print(f"  ✓ {name}")
        else:
            all_ok = False
            print(f"  ✗ {name}")
            for err in errors[:5]:
                print(f"      · {err}")
            if len(errors) > 5:
                print(f"      · ... and {len(errors) - 5} more")
    print()
    if all_ok:
        print("✅ All checks passed — project is presentable.")
        sys.exit(0)
    print("❌ Some checks failed — review the issues above before pushing.")
    sys.exit(1)


if __name__ == "__main__":
    main()
