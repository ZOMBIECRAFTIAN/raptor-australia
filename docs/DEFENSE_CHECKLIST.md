# Defense Checklist - v1.5 Academic Release

## One-minute Positioning

- State that v1.5 is an academic baseline, not a production authority.
- Explain the final architecture: YOLO-assisted localisation plus EfficientNetB4 classification.
- State the active scope: eight Australian raptor species, real dataset, real test split.
- State the headline metrics: accuracy 0.8495, macro-F1 0.8482, app-output ECE 0.0639.

## Evidence To Show

- `README.md`: release scope, setup, usage and limitations.
- `results/test_predictions.csv`: image_path, y_true, y_pred, confidence, top3.
- `results/bootstrap_ci_efficientnet_b4.md`: confidence intervals.
- `results/error_analysis_efficientnet_b4.md`: family-aware error analysis.
- `results/reliability_diagram_efficientnet_b4.png`: calibration evidence.
- `docs/DATASHEET.md`: dataset provenance and risks.
- `docs/MODEL_CARD.md`: intended use, limits and ethical cautions.
- `docs/Australian_Raptor_Thesis_v1_5.docx`: formal thesis manuscript.
- `docs/Australian_Raptor_Thesis_v1_5.pdf`: exported thesis PDF.
- `docs/MASTERS_RESEARCH_PROPOSAL.md`: Master's/MPhil scope and plan.
- `docs/SCIENTIFIC_DEFENSIBILITY.md`: claim limits and threats to validity.
- `docs/MASTERS_PRESENTATION_OUTLINE.md`: presentation structure and speaking order.
- `docs/SPLIT_GOVERNANCE.md`: leakage audit status and stronger v2.0 split plan.
- `docs/MODEL_REGISTRY.md`: checkpoint hash, class order and reproduction commands.
- `docs/LIMITATIONS.md`: claims to avoid and threats to validity.
- `docs/CONTROLLED_DEMO_SET.md`: balanced demo set with easy, difficult and out-of-domain cases.
- `results/top3_utility.md`: top-3 utility for citizen-science use.
- `results/leakage_audit.md`: exact/source/near-duplicate audit.
- `results/yolo_crop_ablation.md`: YOLO-crop ablation status.
- `results/temperature_scaling_efficientnet_b4.json`: calibration before/after.
- `RELEASE_MANIFEST_v1_5.md`: release artefacts and SHA-256 hashes.

## Live Verification

Run these commands before presenting:

```powershell
python notebooks\run_tests.py
python notebooks\healthcheck.py --verbose
python notebooks\export_test_predictions.py
python notebooks\bootstrap_metrics.py --report-md
python notebooks\error_analysis.py
python notebooks\calibration_ece.py
python notebooks\audit_thesis_docx.py
python notebooks\audit_thesis_pdf.py
python notebooks\audit_dataset_leakage.py --max-hamming 4
python notebooks\top3_utility.py
python notebooks\yolo_crop_ablation.py
python notebooks\temperature_scaling.py
python notebooks\build_model_registry.py
python notebooks\build_controlled_demo_set.py
python notebooks\build_release_manifest.py
```

## Questions To Be Ready For

- Why use EfficientNetB4 as the single classifier?
- Why use YOLO if the classifier can process whole images?
- How do you know the dataset, app and model class order are synchronized?
- What does `top3` add for ecological or citizen-science use?
- Why is the AUSLAN component provisional?
- What would make v2.0 stronger scientifically?

## Honest Limitations

- Per-image split rather than group-aware split.
- Eight-species closed-set classification.
- Generic YOLO detector, not a raptor-box fine-tuned detector.
- Dataset likely contains geographic, observer and plumage bias.
- AUSLAN illustrations require Deaf-community validation before authority is claimed.
