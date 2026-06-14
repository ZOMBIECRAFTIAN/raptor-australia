# Claims Matrix

| Claim | Status | Evidence |
|---|---|---|
| The v1.5 classifier covers 8 active species. | Allowed | `gui/app.py::CLASS_ORDER` |
| The classifier is EfficientNetB4. | Allowed | `gui/app.py`, `docs/MODEL_REGISTRY.md` |
| YOLO is integrated as detector/cropper infrastructure. | Allowed | `gui/yolo_detector.py`, `results/yolo_crop_ablation.md` |
| Whole-image v1.5 accuracy is 0.8495. | Allowed | `results/reporte_final.json` |
| Top-3 accuracy is 0.9660. | Allowed | `results/top3_utility.md` |
| The project is production-ready. | Not allowed | Out of scope; see `docs/LIMITATIONS.md` |
| The model replaces expert identification. | Not allowed | Model card and limitations reject this |
| The AUSLAN signs are validated. | Not allowed | Consultation is provisional |
| The v1.5 model covers 14 species. | Not allowed | 14 species is roadmap only |
| YOLO-crop improves current checkpoint accuracy. | Not allowed | Current ablation shows lower accuracy than whole-image |
| A v1.6/v2.0 split should group near-duplicates. | Allowed as recommendation | `docs/SPLIT_GOVERNANCE.md` |

## Short Defence Version

Allowed:

> This is a reproducible 8-species EfficientNetB4 + YOLO research
> baseline with real metrics, top-3 utility, leakage screening and
> documented limitations.

Not allowed:

> This is a final production-grade Australian raptor identification system.
