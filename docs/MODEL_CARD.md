# Model Card — Australian Raptor CNN v1.5

*Following the model-card framework of Mitchell et al. (2019),
"Model Cards for Model Reporting".*

---

## 1. Model Details

- **Project**: Australian Raptor CNN + AUSLAN companion vocabulary.
- **Release**: v1.5 academic baseline.
- **Classifier**: EfficientNetB4, ImageNet-pretrained, with a
  fresh 8-class classification head.
- **Detector/cropper**: YOLO via `ultralytics` when available;
  no alternate detector architecture is active in v1.5.
- **Checkpoint**: `models/best_model.pth`.
- **Author**: Brian Fernandez-Baez, Computer Systems Engineer,
  independent researcher preparing Master's by Research / MPhil
  applications in Australia, with a future PhD pathway.
- **Date**: 2026-06-13.
- **Framework**: PyTorch 2.12+cu130 + torchvision 0.27+cu130.
- **License**: MIT for code; image licensing is documented in
  `docs/DATASHEET.md`.

---

## 2. Intended Use

Primary use is a research-prototype citizen-science aid: given a
photo or video frame of an Australian raptor, the system returns
top-1 species, confidence, and top-3 alternatives, then supports
Darwin Core export for biodiversity records.

The model is **not** intended for conservation enforcement,
rehabilitation decisions, regulatory decisions, or subspecies
identification.

---

## 3. Classes

The validated checkpoint predicts eight species:

1. `aquila_audax`
2. `circus_assimilis`
3. `elanus_axillaris`
4. `falco_cenchroides`
5. `falco_peregrinus`
6. `hieraaetus_morphnoides`
7. `lophoictinia_isura`
8. `tachyspiza_fasciata`

The 14-species expansion is documented in
`docs/SPECIES_ROADMAP.md` but is not claimed as validated in this
model card.

---

## 4. Data

- **Processed split**: 1,992 images.
- **Train / validation / test**: 1,590 / 196 / 206.
- **Sources**: iNaturalist Australia and Atlas of Living
  Australia.
- **Split mechanism**: deterministic per-image split, seed 42.
- **Known caveat**: per-image splitting may permit
  observation-level leakage if multiple photos from the same
  observation occur in different splits.

---

## 5. Metrics

Metrics are computed on the 206-image held-out test set.
Per-image predictions are stored in `results/test_predictions.csv`.

| Metric | Value |
|---|---:|
| Top-1 accuracy | 0.8495 |
| Macro-F1 | 0.8482 |
| Weighted-F1 | 0.8476 |
| Family-level accuracy | 0.9272 |
| Cross-family error rate | 0.0728 |
| Expected Calibration Error | 0.0639 |

Bootstrap 95% confidence intervals with B=1,000:

| Metric | Bootstrap mean | 95% CI |
|---|---:|---|
| Accuracy | 0.8504 | [0.8010, 0.8981] |
| Macro-F1 | 0.8467 | [0.7964, 0.8935] |

Generated artefacts:

- `results/bootstrap_ci_efficientnet_b4.md`
- `results/error_analysis_efficientnet_b4.md`
- `results/calibration_efficientnet_b4.json`
- `results/reliability_diagram_efficientnet_b4.png`

---

## 6. Factors

Expected performance varies by:

- geography: southeast Australia is over-represented;
- pose: perched and side-on birds are easier than distant flight
  images;
- plumage: juvenile and immature birds remain under-represented;
- species set: any raptor outside the eight validated classes is
  out of distribution.

---

## 7. Ethical Notes

- The UI must show alternatives and uncertainty, not only top-1.
- AUSLAN signs are provisional schematic illustrations and must
  not be presented as validated AUSLAN.
- The model should not be used for legally consequential wildlife
  decisions.
- Future publication should include Deaf-community validation and
  a group-aware data split audit.

---

*Document version 1.5.0; last updated 2026-06-07.*
