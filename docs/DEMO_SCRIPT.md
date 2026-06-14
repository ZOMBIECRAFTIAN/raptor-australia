# Demo Script - v1.5 Academic Release

## Demo Objective

Show that the project is now an auditable academic prototype: a single classifier architecture, YOLO adaptive localisation, real metrics, real tests, reproducible analysis artefacts and formal documentation.

## Five-minute Flow

1. Open `README.md` and state the v1.5 scope.
2. Show `gui/app.py::CLASS_ORDER` and confirm the eight active species.
3. Show `gui/yolo_detector.py` and explain that YOLO localises candidate bird regions before classification when available.
4. Open `results/test_predictions.csv` and show the required schema: `image_path,y_true,y_pred,confidence,top3`.
5. Open `results/bootstrap_ci_efficientnet_b4.md`, `results/error_analysis_efficientnet_b4.md` and `results/calibration_efficientnet_b4.json`.
6. Run `python notebooks\run_tests.py`.
7. Run `python notebooks\healthcheck.py --verbose`.
8. Open `docs/Australian_Raptor_Thesis_v1_5.pdf` and `RELEASE_MANIFEST_v1_5.md`.
9. Open `docs/MASTERS_RESEARCH_PROPOSAL.md` and `docs/SCIENTIFIC_DEFENSIBILITY.md`.
10. Show `results/top3_utility.md`, `results/leakage_audit.md`, and `docs/SPLIT_GOVERNANCE.md`.
11. Launch the Flask app and perform one image prediction.
12. Show the controlled demo set in `docs/CONTROLLED_DEMO_SET.md`.
13. Show a Darwin Core export and one feedback log row.
14. Close with the future research bridge: 14+ species, retraining, detector fine-tuning and stronger split governance.

## Talking Points

- v1.5 intentionally keeps one classifier architecture because a Master's baseline should be clear, reproducible and defensible.
- YOLO is included as a localisation layer, not as a substitute for species classification.
- The per-image predictions CSV makes bootstrap, calibration and error analysis reproducible.
- The automated tests protect the project contract: model class order, Flask routes, Darwin Core, i18n, feedback and healthcheck.
- The AUSLAN assets are framed as provisional until community validation occurs.

## Last Slide Message

This release is not claiming final ecological authority. It is claiming a reproducible baseline with transparent metrics, explicit limitations and a credible path to a stronger v2.0 study.
