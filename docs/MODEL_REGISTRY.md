# Model Registry

## raptor-efficientnetb4-v1.5

- Checkpoint: `models/best_model.pth`
- SHA-256: `855be2a4a6a9a4dc7445848e946bb7f0a400e0ec78d9160faa6c96c27021fc67`
- Architecture: EfficientNetB4
- Detector/cropper: YOLOv8n COCO bird detector
- Detector weights: `models/yolov8n.pt`
- Detector SHA-256: `f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36`
- Crop policy: adaptive
- Calibration temperature: 0.6934510469436646
- Active classes: 8
- Test images: 206
- Accuracy: 0.8495
- Macro-F1: 0.8482
- Weighted-F1: 0.8476

## Class Order

0. `aquila_audax`
1. `circus_assimilis`
2. `elanus_axillaris`
3. `falco_cenchroides`
4. `falco_peregrinus`
5. `hieraaetus_morphnoides`
6. `lophoictinia_isura`
7. `tachyspiza_fasciata`

## Reproduction Commands

```powershell
python notebooks/export_test_predictions.py
python notebooks/update_final_report.py
python notebooks/bootstrap_metrics.py --report-md
python notebooks/error_analysis.py
python notebooks/calibration_ece.py
python notebooks/top3_utility.py
python notebooks/yolo_crop_ablation.py
python notebooks/run_tests.py
python notebooks/healthcheck.py --verbose
```
