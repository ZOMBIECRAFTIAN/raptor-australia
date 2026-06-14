# Datasheet — Australian Raptor Image Dataset v1.5

*Following the datasheet template of Gebru et al. (2021),
"Datasheets for Datasets".*

---

## 1. Motivation

The dataset supports fine-grained image classification of
Australian raptors for a citizen-science research prototype. It
is designed to demonstrate an end-to-end pipeline:

1. collect open biodiversity imagery;
2. curate image quality and bird presence;
3. train an EfficientNetB4 species classifier;
4. use YOLO-assisted localisation in the web application;
5. export user-confirmed observations in Darwin Core format.

The dataset was created by Brian Fernandez-Baez as an
independent research prototype for prospective Master's by
Research / MPhil applications in Australia, with a future PhD
continuation path. No external funding or university affiliation
is claimed for this release.

---

## 2. Composition

The validated v1.5 dataset contains eight species:

| Species key | Common name | Processed test support |
|---|---|---:|
| `aquila_audax` | Wedge-tailed Eagle | 23 |
| `circus_assimilis` | Spotted Harrier | 32 |
| `elanus_axillaris` | Black-shouldered Kite | 27 |
| `falco_cenchroides` | Nankeen Kestrel | 22 |
| `falco_peregrinus` | Peregrine Falcon | 23 |
| `hieraaetus_morphnoides` | Little Eagle | 22 |
| `lophoictinia_isura` | Square-tailed Kite | 25 |
| `tachyspiza_fasciata` | Brown Goshawk | 32 |

The processed split contains 1,992 images:

| Split | Images |
|---|---:|
| Train | 1,590 |
| Validation | 196 |
| Test | 206 |

The local cleaned `dataset/raw/` folders currently contain 2,106
images. The processed split is smaller because preprocessing
validates, crops/resizes and writes only images that pass the
current training criteria.

Each instance is a still RGB image labelled by species key using
PyTorch `ImageFolder` alphabetical class ordering. The active
class order is committed in `gui/app.py::CLASS_ORDER`.

---

## 3. Collection Process

Images come from public biodiversity platforms:

- iNaturalist Australia, research-grade observations;
- Atlas of Living Australia biocache image records.

Download scripts use public APIs, polite rate limiting and
identifying user-agent strings. The dataset image files are not
redistributed in this repository; scripts and metadata are
provided so the dataset can be regenerated under upstream terms.

---

## 4. Preprocessing And Curation

The current v1.5 training pipeline:

- validates image readability;
- discards images below the minimum usable resolution;
- centre-crops and resizes to 380 x 380 for EfficientNetB4;
- writes deterministic train/validation/test splits with seed 42.

YOLO is now the preferred detector/cropper for app-side
localisation and future curation passes. Earlier curation used
torchvision COCO bird detection; that remains available as a
fallback in the app when YOLO weights or `ultralytics` are not
installed.

Rejected images are moved to `dataset/raw_archive/` rather than
deleted, preserving auditability.

---

## 5. Recommended Use

Appropriate uses:

- Australian raptor fine-grained classification research;
- detector + classifier pipeline experiments;
- citizen-science UI prototyping;
- Darwin Core export demonstrations;
- thesis-scale analysis of uncertainty, calibration and
  taxonomy-aware errors.

Inappropriate uses:

- conservation enforcement;
- wildlife rehabilitation decisions;
- subspecies claims;
- any legally consequential decision.

---

## 6. Biases And Limitations

- **Geographic bias**: southeast Australia is over-represented.
- **Photographer bias**: clear, perched and side-on photos are
  easier and more common than difficult field conditions.
- **Per-image split**: future versions should use group-aware
  splits by observation or observer to reduce leakage risk.
- **Closed-set assumption**: the v1.5 classifier only recognises
  eight classes; all other raptors are out of distribution.

---

## 7. Maintenance

The v1.5 dataset is maintained through:

- `docs/SPECIES_ROADMAP.md` for species expansion;
- `docs/TAXONOMY_VERSIONING.md` for taxonomic changes;
- `results/test_predictions.csv` for per-image evaluation;
- `docs/MODEL_CARD.md` for model-specific reporting.

The next dataset milestone is v2.0: 14 species using the same
YOLO + EfficientNetB4 pipeline, with a new datasheet only after
the expanded split and checkpoint are validated.

---

*Last updated: 2026-06-07; release v1.5.*
