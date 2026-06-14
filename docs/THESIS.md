# Thesis Draft — Australian Raptor CNN + AUSLAN

**Working title:** YOLO-Assisted Deep Learning for Australian
Raptor Identification with Accessible Citizen-Science Interfaces

**Author:** Brian Fernandez-Baez  
**Release:** v1.5 academic baseline  
**Date:** 2026-06-07

---

## Abstract

This thesis presents a research prototype for Australian raptor
identification under citizen-science image conditions. The system
combines YOLO-based bird localisation with an EfficientNetB4
classifier trained on eight Australian raptor species from
iNaturalist Australia and the Atlas of Living Australia. The
prototype also implements a multilingual Flask interface, top-3
species alternatives, Darwin Core export, feedback logging and
provisional AUSLAN motion illustrations. On a 206-image held-out
test split, the classifier reaches 84.95% top-1 accuracy and
0.8482 macro-F1. Bootstrap confidence intervals, calibration
analysis, family-level error analysis and Grad-CAM diagnostics are
reported to support reproducibility and scientific caution.

---

## Chapter 1 — Introduction

Australian raptors are ecologically important apex and meso-
predators, but reliable species identification remains difficult
for non-specialists. Citizen-science platforms can expand
monitoring coverage, yet visual identification, interoperability
with biodiversity data standards and accessibility for Deaf
participants remain open problems.

This thesis asks whether a compact, reproducible computer-vision
pipeline can support Australian raptor identification while also
exposing records in Darwin Core format and documenting a pathway
for participatory AUSLAN validation.

### Research Questions

1. Can a YOLO + EfficientNetB4 pipeline identify eight Australian
   raptor species with useful accuracy under citizen-science image
   conditions?
2. Can the prediction workflow produce auditable per-image
   predictions and Darwin Core-compatible records?
3. How should provisional AUSLAN signs be framed so they invite
   participatory validation without claiming authority?

### Contributions

- A validated eight-species v1.5 raptor classification baseline.
- A YOLO-assisted localisation path for images and video frames.
- Per-image evaluation outputs in `results/test_predictions.csv`.
- Bootstrap, calibration and taxonomy-aware error analyses.
- A multilingual Flask app with feedback and Darwin Core export.
- A documented AUSLAN consultation protocol.

---

## Chapter 2 — Literature Review

The thesis draws on four bodies of work:

- fine-grained bird classification and transfer learning;
- object detection for ecological image analysis;
- citizen-science biodiversity infrastructure, including ALA,
  GBIF and Darwin Core;
- accessibility, AUSLAN and participatory design.

EfficientNetB4 is used as the single classifier because it offers
a strong accuracy/compute balance at 380 px inputs. YOLO is used
for localisation and candidate cropping, but the current release
uses an adaptive policy because crop-only inference did not improve
the held-out checkpoint.

---

## Chapter 3 — Methodology

### Dataset

The v1.5 processed dataset contains 1,992 images across eight
species:

| Split | Images |
|---|---:|
| Train | 1,590 |
| Validation | 196 |
| Test | 206 |

The active class order is fixed in `gui/app.py::CLASS_ORDER`.
The split is deterministic with seed 42.

### Pipeline

1. YOLO detects bird regions in an uploaded image or sampled video
   frame.
2. Each crop is resized and normalised for EfficientNetB4.
3. EfficientNetB4 predicts one of eight species.
4. The UI displays top-1, confidence and top-3 alternatives.
5. User feedback and Darwin Core exports are written to CSV.

### Reproducibility

Reproducibility artefacts:

- `requirements.txt`
- `environment.yml`
- `Dockerfile`
- `.github/workflows/ci.yml`
- `notebooks/healthcheck.py`
- `tests/test_project_integrity.py`
- `docs/DATASHEET.md`
- `docs/MODEL_CARD.md`

---

## Chapter 4 — Results

### Global Metrics

| Metric | Value |
|---|---:|
| Test images | 206 |
| Top-1 accuracy | 0.8495 |
| Macro-F1 | 0.8482 |
| Weighted-F1 | 0.8476 |
| ECE | 0.0639 |
| Family-level accuracy | 0.9272 |

### Bootstrap Confidence Intervals

| Metric | Bootstrap mean | 95% CI |
|---|---:|---|
| Accuracy | 0.8504 | [0.8010, 0.8981] |
| Macro-F1 | 0.8467 | [0.7964, 0.8935] |

### Error Analysis

The model reaches 92.72% family-level accuracy. Cross-family
errors account for 15 of 206 test images (7.3%). The most common
confusion is `tachyspiza_fasciata` predicted as `elanus_axillaris`,
followed by `falco_cenchroides` predicted as `elanus_axillaris`.

### Figures

Recommended thesis figures:

- `results/gradcam_mosaic.png`
- `results/confusion_family_efficientnet_b4.png`
- `results/reliability_diagram_efficientnet_b4.png`
- `results/leakage_near_duplicate_pairs.jpg`

---

## Chapter 5 — Software And Accessibility

The Flask application implements:

- image upload and prediction;
- video-frame sampling and bird detection;
- top-3 alternatives;
- feedback logging;
- out-of-domain feedback;
- Darwin Core export;
- 10-language UI support;
- provisional AUSLAN sign illustrations.

The AUSLAN component is explicitly provisional. No sign is claimed
as validated AUSLAN until reviewed through Deaf-community
consultation. The contribution is therefore a process and
prototype contribution, not an authoritative vocabulary.

---

## Chapter 6 — Discussion And Conclusion

The v1.5 release demonstrates that a modest, reproducible
YOLO-assisted EfficientNetB4 pipeline can support Australian
raptor identification with useful but imperfect performance. The
system is strong enough for a research prototype and scholarship
portfolio, but not for legally consequential deployment.

Key limitations:

- per-image rather than group-aware splitting;
- closed-set eight-species output;
- under-representation of juveniles and remote regions;
- provisional, unvalidated AUSLAN signs;
- detector weights are generic COCO weights, not raptor-specific.

Future work should prioritise group-aware splits, YOLO fine-tuning
on raptor boxes, the 14-species v2.0 expansion, and participatory
AUSLAN validation.

---

## Appendices

### Appendix A — Dataset Datasheet

See `docs/DATASHEET.md`.

### Appendix B — Model Card

See `docs/MODEL_CARD.md`.

### Appendix C — Per-Image Predictions

See `results/test_predictions.csv`.

### Appendix D — Statistical Artefacts

- `results/bootstrap_ci_efficientnet_b4.md`
- `results/error_analysis_efficientnet_b4.md`
- `results/calibration_efficientnet_b4.json`

### Appendix E — Release Package

- `docs/Australian_Raptor_Thesis_v1_5.docx`
- `docs/Australian_Raptor_Thesis_v1_5.pdf`
- `results/thesis_docx_audit.json`
- `results/thesis_pdf_audit.json`
- `RELEASE_MANIFEST_v1_5.md`

### Appendix F — AUSLAN Consultation

See `docs/auslan_consultation/`.

---

## Bibliography Seed

- Efron, B. (1979). Bootstrap methods: another look at the
  jackknife.
- Gebru, T. et al. (2021). Datasheets for datasets.
- Guo, C. et al. (2017). On calibration of modern neural networks.
- Mitchell, M. et al. (2019). Model cards for model reporting.
- Selvaraju, R. R. et al. (2017). Grad-CAM.
- Tan, M. and Le, Q. (2019). EfficientNet.
- Van Horn, G. et al. (2018). The iNaturalist species
  classification and detection dataset.
