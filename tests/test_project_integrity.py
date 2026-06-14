from __future__ import annotations

import csv
import importlib
import io
import os
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GUI_DIR = ROOT / "gui"


def load_app(monkeypatch):
    monkeypatch.setenv("RAPTOR_LIGHTWEIGHT", "1")
    sys.path.insert(0, str(GUI_DIR))
    if "app" in sys.modules:
        return importlib.reload(sys.modules["app"])
    return importlib.import_module("app")


def test_class_order_matches_dataset_and_results(monkeypatch):
    app_mod = load_app(monkeypatch)

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
    assert app_mod.CLASS_ORDER == expected
    assert app_mod.NUM_CLASSES == len(expected)
    assert [app_mod.SPECIES_INFO[k]["class_idx"] for k in expected] == list(
        range(len(expected))
    )

    test_dir = ROOT / "dataset" / "processed" / "test"
    if test_dir.exists():
        assert sorted(p.name for p in test_dir.iterdir() if p.is_dir()) == expected

    report = ROOT / "results" / "reporte_final.json"
    if report.exists() and test_dir.exists():
        import json

        data = json.loads(report.read_text(encoding="utf-8"))
        n_test = sum(
            1
            for sp in test_dir.iterdir()
            if sp.is_dir()
            for p in sp.iterdir()
            if p.is_file()
        )
        assert data["total_test_images"] == n_test


def test_i18n_covers_active_species(monkeypatch):
    app_mod = load_app(monkeypatch)
    from species_data_i18n import get_species_data
    from i18n import LANGUAGES

    for lang in LANGUAGES:
        localized = get_species_data(lang)
        for key in app_mod.CLASS_ORDER:
            assert key in localized
            assert localized[key]["common_name"]
            assert localized[key]["diagnostic"]


def test_flask_routes_render_in_lightweight_mode(monkeypatch, tmp_path):
    app_mod = load_app(monkeypatch)
    monkeypatch.setattr(app_mod, "PROJECT_ROOT", tmp_path)
    (tmp_path / "results").mkdir()
    app_mod.app.config["TESTING"] = True

    client = app_mod.app.test_client()
    for route in ["/", "/species", "/data"]:
        resp = client.get(route)
        assert resp.status_code == 200
        assert len(resp.data) > 500


def test_identify_route_uses_dummy_prediction_in_lightweight_mode(
    monkeypatch, tmp_path
):
    app_mod = load_app(monkeypatch)
    monkeypatch.setattr(app_mod, "PROJECT_ROOT", tmp_path)
    app_mod.app.config["TESTING"] = True

    img = Image.new("RGB", (32, 32), color=(200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = app_mod.app.test_client().post(
        "/identify",
        data={"image": (buf, "test.png")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["species_key"] == app_mod.CLASS_ORDER[0]
    assert len(payload["top3"]) == 3


def test_feedback_logs_to_project_results(monkeypatch, tmp_path):
    app_mod = load_app(monkeypatch)
    monkeypatch.setattr(app_mod, "PROJECT_ROOT", tmp_path)
    app_mod.app.config["TESTING"] = True

    resp = app_mod.app.test_client().post(
        "/feedback",
        json={
            "predicted_key": "aquila_audax",
            "predicted_name": "Wedge-tailed Eagle",
            "correct_key": "falco_peregrinus",
            "correct_name": "Peregrine Falcon",
            "confidence": 72.4,
        },
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "saved"

    log_path = tmp_path / "results" / "feedback_log.csv"
    assert log_path.exists()
    with open(log_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["predicted_key"] == "aquila_audax"
    assert rows[0]["correct_key"] == "falco_peregrinus"


def test_darwin_core_mapping(monkeypatch):
    app_mod = load_app(monkeypatch)
    rows = app_mod._to_dwc_rows([
        {
            "timestamp": "2026-06-07T12:00:00",
            "species_key": "aquila_audax",
            "common_name": "Wedge-tailed Eagle",
            "scientific_name": "Aquila audax",
            "confidence": "91.0",
            "latitude": "-33.86",
            "longitude": "151.20",
            "notes": "test",
            "observer_confirmed": "true",
        }
    ])
    assert rows[0]["basisOfRecord"] == "HumanObservation"
    assert rows[0]["eventDate"] == "2026-06-07"
    assert rows[0]["scientificName"] == "Aquila audax"
    assert "EfficientNetB4" in rows[0]["identifiedBy"]
    assert "YOLO" in rows[0]["identifiedBy"]


def test_yolo_wrapper_imports_without_ultralytics():
    sys.path.insert(0, str(GUI_DIR))
    mod = importlib.import_module("yolo_detector")
    assert mod.COCO_BIRD_CLASS_ID == 14
    assert hasattr(mod, "YoloBirdDetector")


def test_single_image_yolo_crop_path(monkeypatch):
    app_mod = load_app(monkeypatch)

    class Box:
        bbox = [50, 50, 80, 80]
        confidence = 0.91
        source = "yolo"

    class Detector:
        def detect(self, _img):
            return [Box()]

    monkeypatch.setattr(app_mod, "_lazy_yolo_detector", lambda: Detector())

    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    crop, meta = app_mod._select_yolo_crop(img)

    assert crop.size == (40, 40)
    assert meta == {
        "detector": "yolo",
        "bbox": [45, 45, 85, 85],
        "bbox_score": 0.91,
    }


def test_health_route_reports_runtime_contract(monkeypatch):
    app_mod = load_app(monkeypatch)
    app_mod.app.config["TESTING"] = True

    resp = app_mod.app.test_client().get("/health")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["status"] == "ok"
    assert payload["model_version"] == app_mod.MODEL_VERSION
    assert payload["classifier"] == "EfficientNetB4"
    assert payload["detector"] == "YOLO"
    assert payload["active_species_count"] == len(app_mod.CLASS_ORDER)
    assert payload["lightweight_mode"] is True
    assert payload["model_loaded"] is False
    assert "cuda_available" in payload