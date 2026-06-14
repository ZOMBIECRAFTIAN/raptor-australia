# Methodology — Australian Raptor CNN v1.5

*Formal methodology write-up for a Master's-level research
prototype with a future doctoral continuation path. Author:
Brian Fernandez-Baez, independent researcher.*

---

## 1. Problem Framing

The project addresses closed-set, fine-grained visual
classification of eight Australian raptor species under
citizen-science image conditions. The deployed system is a
two-stage computer-vision pipeline:

1. **YOLO bird localisation** for images or sampled video frames;
2. **EfficientNetB4 species classification** over the validated
   eight-class set.

The user-facing Flask app reports top-1 prediction, confidence,
top-3 alternatives, species information, provisional AUSLAN
illustrations and Darwin Core export.

---

## 2. Data

### 2.1 Sources

Images are drawn from iNaturalist Australia and the Atlas of
Living Australia. The project does not redistribute raw image
data; it ships scripts, metadata and documentation so the dataset
can be regenerated under upstream licensing terms.

### 2.2 Current Split

The v1.5 processed split contains 1,992 images:

| Split | Images |
|---|---:|
| Train | 1,590 |
| Validation | 196 |
| Test | 206 |

The active class order is:

`aquila_audax`, `circus_assimilis`, `elanus_axillaris`,
`falco_cenchroides`, `falco_peregrinus`,
`hieraaetus_morphnoides`, `lophoictinia_isura`,
`tachyspiza_fasciata`.

### 2.3 Curation

Images are validated for readability and minimum usable
resolution. The current app uses YOLO as the bird
detector/cropper. When YOLO dependencies or weights are
unavailable, the workflow degrades to whole-image classification
or non-detector heuristics rather than switching detector
architecture.

---

## 3. Model

### 3.1 Detector

YOLO is used for bird localisation, especially in video and
multi-bird scenes. The detector returns bounding boxes for the
COCO `bird` class; each crop is sent to the classifier. YOLO is
not used as the species classifier in v1.5.

### 3.2 Classifier

The classifier is EfficientNetB4 initialised from ImageNet
weights and trained with a fresh 8-class head. EfficientNetB4 is
kept as the single architecture for the academic release because
it is accurate enough for the prototype, already validated in
the local checkpoint, and simpler to defend than changing the
research question around backbone selection.

### 3.3 Training Regime

- Stage 1: train the new classification head with the backbone
  frozen.
- Stage 2: unfreeze late backbone layers and fine-tune at a
  lower learning rate.
- Optimiser: AdamW.
- Loss: class-weighted cross entropy with label smoothing in the
  retraining script.
- Seed: 42.
- Input size: 380 x 380.

---

## 4. Evaluation

Evaluation is based on `results/test_predictions.csv`, generated
by `notebooks/export_test_predictions.py` or by `notebooks/retrain.py`.
Each row contains:

`image_path,y_true,y_pred,confidence,top3`.

Primary metrics:

- top-1 accuracy;
- macro-F1;
- weighted-F1;
- per-species precision, recall and F1.

Uncertainty and diagnostic metrics:

- 95% percentile bootstrap confidence intervals with B=1,000;
- Expected Calibration Error with 10 confidence bins;
- Accipitridae/Falconidae family-level confusion;
- top confusion pairs;
- Grad-CAM visual inspection.

Current v1.5 held-out test results:

| Metric | Value |
|---|---:|
| Test images | 206 |
| Accuracy | 0.8495 |
| Macro-F1 | 0.8482 |
| Bootstrap accuracy CI | [0.8010, 0.8981] |
| Bootstrap macro-F1 CI | [0.7964, 0.8935] |
| Family-level accuracy | 0.9272 |
| ECE | 0.0639 |

---

## 5. Software Validation

The project now ships real automated tests under `tests/`:

- `CLASS_ORDER` synchronisation with dataset and results;
- Flask route rendering in lightweight mode;
- image-identification endpoint plumbing;
- feedback logging;
- Darwin Core mapping;
- i18n coverage for all active species;
- YOLO wrapper importability.

`notebooks/healthcheck.py` runs syntax, JSON, release sync,
YOLO wrapper, template, YAML and pytest checks. CI calls the same
healthcheck in `RAPTOR_LIGHTWEIGHT=1` mode so GitHub Actions does
not need to download model weights or install PyTorch.

---

## 6. Threats To Validity

- **Observation-level leakage**: the split is per-image, not
  per-observation. A future group split is required before
  stronger ecological claims.
- **Closed-set limitation**: the model cannot identify species
  outside the eight validated classes.
- **Calibration**: app-output ECE is mild (0.0639) but confidence should
  still be presented as model confidence, not truth probability.
- **Geographic bias**: southeast Australia is over-represented.
- **AUSLAN validation**: sign illustrations are provisional until
  validated with the Deaf community.

---

## 7. Ethics

The model is for research and citizen-science support only. It
must not be used for legally consequential conservation decisions
or wildlife-care decisions. The AUSLAN component is framed as a
participatory-design protocol, not an authoritative vocabulary.
