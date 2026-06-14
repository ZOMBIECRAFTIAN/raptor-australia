# 🦅 Australian Raptor CNN + AUSLAN

> Deep-learning identification of Australian birds of prey using
> citizen-science imagery, paired with a provisional AUSLAN
> sign-language vocabulary for accessibility.
>
> **Master's-level research release prepared for prospective
> Master's by Research / MPhil applications in Australia, with a
> future PhD continuation path.** This repository is a working
> research prototype; it is *not* affiliated with, endorsed by,
> or part of an enrolled program at any Australian university.

[![CI](https://github.com/ZOMBIECRAFTIAN/raptor-australia/actions/workflows/ci.yml/badge.svg)](https://github.com/ZOMBIECRAFTIAN/raptor-australia/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![PyTorch 2.12+cu130](https://img.shields.io/badge/PyTorch-2.12%2Bcu130-EE4C2C.svg)](https://pytorch.org/)
[![Accuracy 84.95%](https://img.shields.io/badge/accuracy-84.95%25-brightgreen.svg)](results/reporte_final.json)
[![F1-macro 0.848](https://img.shields.io/badge/F1--macro-0.848-green.svg)](results/reporte_final.json)
[![Status: research prototype](https://img.shields.io/badge/status-research%20prototype-orange.svg)]()

---

## Why Australia?

Australia hosts approximately 24 diurnal raptor species,
including taxa endemic to its biogeographic region (e.g. the
nominate *Aquila audax audax* and its threatened Tasmanian
sub-species *A. a. fleayi*). The continent experienced its
largest documented ecological disturbance during the
**Black Summer bushfires (2019-2020)** — an estimated 3 billion
vertebrates affected and 18.6 million hectares burnt (Ward et al.,
*Nature Ecology & Evolution*, 2020) — and continued monitoring of
apex predators is a stated national research priority of the
Department of Climate Change, Energy, the Environment and Water
(DCCEEW, 2023, *Threatened Species Action Plan 2022-2032*).

These three factors — biological singularity, continental scale
of recent disturbance, and clear national policy priorities —
make Australia the most suitable context in which to apply
computer-vision tools to raptor monitoring.

---

## Conservation relevance

Raptors are widely used indicators of ecosystem health
(Sergio et al., *Annual Review of Ecology, Evolution and
Systematics*, 2006). Of the eight species in the current model:

- *Lophoictinia isura* (Square-tailed Kite) is listed as
  **Vulnerable under the EPBC Act 1999**.
- *Aquila audax fleayi* (Tasmanian sub-species) is listed as
  **Endangered under the EPBC Act 1999**.
- *Circus assimilis* (Spotted Harrier) is listed as Vulnerable
  in NSW.

Faster and lower-cost identification supports two operational
needs identified in the DCCEEW action plan: rapid post-fire
fauna surveys, and sustained citizen-science contribution to the
Atlas of Living Australia (ALA).

---

## Research gap

Despite mature CNN tooling for general bird identification
(e.g. *Merlin*, *iNaturalist Seek*), three gaps remain for the
Australian raptor context specifically:

1. **No publicly released raptor-specific Australian benchmark**
   exists with reproducible splits and per-species metrics.
2. **Disability-inclusive design** is absent from existing tools.
   No widely adopted bird-identification app currently ships
   AUSLAN signs or sign-language alternatives to spoken species
   names.
3. **Interoperability with Australian biodiversity infrastructure**
   (ALA, GBIF, Darwin Core) is rarely demonstrated end-to-end
   from a citizen-science capture interface.

This repository is a working prototype that addresses all three
gaps, intended as evidence for a prospective Master's by Research
/ MPhil application in computer vision for conservation in
Australia, while leaving a clear future PhD pathway.

---

## Target species (current validated model)

The validated model recognises **eight raptor species** chosen
for ecological relevance and minimum data availability:

| Common name | Scientific name | EPBC status |
|---|---|---|
| Wedge-tailed Eagle | *Aquila audax* | Not listed (A.a.fleayi: Endangered) |
| Peregrine Falcon | *Falco peregrinus macropus* | Not listed |
| Spotted Harrier | *Circus assimilis* | Vulnerable (NSW) |
| Brown Goshawk | *Tachyspiza fasciata* (formerly *Accipiter*) | Not listed |
| Nankeen Kestrel | *Falco cenchroides* | Not listed |
| Black-shouldered Kite | *Elanus axillaris* | Not listed |
| Square-tailed Kite | *Lophoictinia isura* | **Vulnerable (EPBC)** |
| Little Eagle | *Hieraaetus morphnoides* | Not listed |

Per-species precision, recall and F1 are written to
`results/reporte_final.json` after each training run.

A proposed expansion to 14 species (adding *Falco berigora*,
*Haliaeetus leucogaster*, *Haliastur indus*, *H. sphenurus*,
*Milvus migrans*, and *Tachyspiza novaehollandiae*) is
described in [`docs/SPECIES_ROADMAP.md`](docs/SPECIES_ROADMAP.md);
the data-pipeline code is already in place for that expansion,
but the validated metrics in this README correspond to the
**8-species** baseline.

---

## Dataset and data sources

The dataset is constructed from two open APIs:

- **iNaturalist** (v1 API) — Research-Grade observations filtered
  to AU geography and the target taxa; only CC-BY-NC or CC0
  images are downloaded.
- **Atlas of Living Australia** (ALA biocache) — supplementary
  occurrences including older museum records.

The current validated v1.5 release uses an **8-species processed
split of 1,992 images**: 1,590 train, 196 validation and 206
held-out test images. The split is deterministic, seeded with
42, and stored under `dataset/processed/`.

YOLO is now the preferred detector/cropper for app-side bird
localisation and future curation passes. The released
EfficientNetB4 checkpoint remains the species classifier.

Full provenance, licences, sampling biases, and known limitations
are documented in [`docs/DATASHEET.md`](docs/DATASHEET.md),
following the framework of Gebru et al. (2021) *Datasheets for
Datasets*.

Academic delivery artefacts are also included:
[`docs/THESIS.md`](docs/THESIS.md),
[`docs/Australian_Raptor_Thesis_v1_5.docx`](docs/Australian_Raptor_Thesis_v1_5.docx),
[`docs/Australian_Raptor_Thesis_v1_5.pdf`](docs/Australian_Raptor_Thesis_v1_5.pdf),
[`docs/DEFENSE_CHECKLIST.md`](docs/DEFENSE_CHECKLIST.md), and
[`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). Master's framing is
captured in [`docs/MASTERS_RESEARCH_PROPOSAL.md`](docs/MASTERS_RESEARCH_PROPOSAL.md),
[`docs/SCIENTIFIC_DEFENSIBILITY.md`](docs/SCIENTIFIC_DEFENSIBILITY.md), and
[`docs/MASTERS_PRESENTATION_OUTLINE.md`](docs/MASTERS_PRESENTATION_OUTLINE.md).
Additional scientific QA artefacts include
[`docs/SPLIT_GOVERNANCE.md`](docs/SPLIT_GOVERNANCE.md),
[`docs/MODEL_REGISTRY.md`](docs/MODEL_REGISTRY.md),
[`docs/LIMITATIONS.md`](docs/LIMITATIONS.md), and
[`docs/CONTROLLED_DEMO_SET.md`](docs/CONTROLLED_DEMO_SET.md).
The release hash manifest is in
[`RELEASE_MANIFEST_v1_5.md`](RELEASE_MANIFEST_v1_5.md).

---

## Atlas of Living Australia integration

ALA is queried with a polite rate-limited downloader
(`notebooks/download_ala_images.py`) using only the standard-
library HTTP client, an identifying `User-Agent` header, and a
multi-strategy taxonomy fallback (`lsid → species → genus +
specificEpithet`) that handles the IOC 2024 *Accipiter →
Tachyspiza* reclassification.

The dataset is not redistributed; the **scripts** are released
so any third party can regenerate it under ALA's data-use terms.

---

## Darwin Core export

Every observation captured by the Flask application can be
exported in **Darwin Core** (DwC) CSV format. The export endpoint
maps the internal observation schema to the TDWG-controlled
vocabulary used by ALA / GBIF for biodiversity-data exchange:

| DwC term | Source field |
|---|---|
| `scientificName` | `species` |
| `eventDate` | ISO timestamp |
| `decimalLatitude` / `decimalLongitude` | optional GPS |
| `identificationVerificationStatus` | "PredictedAutomated" |
| `identifiedBy` | this repository + version |
| `basisOfRecord` | `HumanObservation` |

The mapping logic lives in `gui/app.py::_to_dwc_rows()` and the
file is downloadable from the `/data` dashboard.

---

## AI methodology

### Architecture

EfficientNetB4 (Tan & Le, *ICML* 2019) initialised from
ImageNet-1k pretrained weights, with a fresh
`Linear(1792 → 8)` classification head.

Why EfficientNetB4? Best precision-to-compute ratio in the
benchmarks of the published literature for fine-grained bird
classification at the 380-px input typical of citizen-science
photographs.

### Two-stage transfer learning

- **Stage 1 (10 epochs)** — backbone frozen, only the new head
  trained at learning rate 1 × 10⁻³.
- **Stage 2 (20 epochs)** — late blocks unfrozen, whole network
  fine-tuned at 1 × 10⁻⁴.

Optimiser AdamW (weight decay 1 × 10⁻⁴), cosine annealing
scheduler with one warm restart, batch size 8, fixed seed 42.

Train-time augmentations: random horizontal flip, random rotation
±15°, colour-jitter, random erasing. Validation/test splits
receive no augmentation.

### YOLO-assisted detection

YOLO is used as the detector/cropper before species
classification. The app first localises bird regions in video
frames or images, then sends the crop to the EfficientNetB4
classifier. If the optional `ultralytics` package or local YOLO
weights are unavailable, the app falls back to the previous
torchvision COCO bird detector so the demo remains usable.

### Interpretability

Grad-CAM (Selvaraju et al., 2017) heat-maps are generated for
diagnostic verification that the model attends to morphological
features (wings, tail, body silhouette) rather than to background
cues. See `notebooks/gradcam.py` and the thesis-ready 4×2 mosaic
in `notebooks/gradcam_mosaic.py`.

---

## Evaluation metrics

The validated EfficientNetB4 model (8 species, iNaturalist + ALA
expanded training set) achieves the following on the held-out
test split:

| Metric | Value | Interpretation |
|---|---|---|
| **Top-1 Accuracy** | **84.95 %** | Proportion of test images whose top-1 prediction matches the true label. |
| **Macro-F1** | **0.8482** | Harmonic mean of precision and recall, averaged equally across the 8 classes. |
| Weighted-F1 | 0.8476 | Same as macro-F1 but weighted by class support. |
| Architecture | EfficientNetB4 | 19 M parameters, ImageNet pretrained. |
| Training images | 1,590 | Deterministic 80 % split, plus on-the-fly augmentation. |
| Validation / Test | 196 / 206 | Held-out validation and test partitions. |
| Bootstrap 95 % CI | Acc. [0.8010, 0.8981]; macro-F1 [0.7964, 0.8935] | Computed from `results/test_predictions.csv` with B=1,000. |
| Calibration | ECE 0.0639 | Current app-prediction confidence from 10-bin reliability analysis. Temperature-scaling experiment: 0.0592 -> 0.0529 on raw logits. |
| Family-level accuracy | 92.72 % | Accipitridae/Falconidae grouped confusion. |

### What these numbers mean academically

- **Accuracy of 84.95 %** in an 8-class problem is well above the
  random baseline (12.5 %) and the majority-class baseline
  (≈ 14 %). It indicates that the model has learned visual
  discriminators meaningful at species level, but it leaves
  roughly one in seven test images mis-classified — a level of
  error that supports the proposed UI design of always showing
  top-3 alternatives plus an explicit "I'm not sure" feedback
  option, rather than presenting the top-1 label as authoritative.
- **Macro-F1 of 0.8482** indicates balanced performance across the
  eight species rather than the model exploiting one or two
  high-support classes; this is the preferred metric on
  conservation-equity grounds because a rare species
  mis-identification carries higher ecological cost than a common
  one.
- The drop from an earlier iNaturalist-only checkpoint
  (~80 % accuracy on its smaller, easier test set) reflects a
  **harder evaluation distribution** — the ALA-expanded test set
  contains habitat shots, juveniles in atypical plumage, and
  museum-record photographs absent from the iNat-only model's
  test set. The current numbers are therefore an honest
  characterisation of citizen-science conditions, not a
  regression.

Per-image predictions are written to `results/test_predictions.csv`
with `image_path,y_true,y_pred,confidence,top3`. Bootstrap CIs,
calibration and taxonomy-aware error analysis are generated from
that single auditable file.

---

## Current limitations

This is a research prototype and should be read as such.

1. **Geographic bias.** ~75 % of iNaturalist Australian
   observations are from south-east Australia (NSW + VIC + ACT).
   Performance in the NT, WA and remote arid zones is expected
   to be lower.
2. **Plumage-stage coverage.** Juveniles and immature plumages
   are under-represented for several species.
3. **Per-image splitting.** The train/val/test split is
   per-image rather than per-observer or per-observation, so
   there is a residual risk of observation-level leakage.
   Group-shuffle splits are flagged as future work.
4. **8-species scope.** The validated model recognises only the
   8 species above. An observed raptor outside that set will be
   forced into one of those classes; the UI exposes an explicit
   "Other — not in 8 species" feedback class to mitigate this.
5. **Calibration is mild but not perfect.** The current app-output ECE is
   0.0639, so displayed confidence is useful but should still be
   treated as model confidence, not biological certainty.
6. **AUSLAN signs are provisional.** They are programmatically-
   generated schematic illustrations of a proposed motion, NOT
   validated AUSLAN. See the AUSLAN section below.

---

## Master's relevance

This repository is positioned as evidence for prospective
Master's by Research / MPhil applications in Australian
universities working at the intersection of computer vision,
conservation biology, and inclusive design (e.g. University of
Queensland CBCS, ANU Fenner School, UNSW Centre for Ecosystem
Science, Monash SEAE, James Cook University TESS). It also
defines a credible bridge to later PhD work. It demonstrates:

- An end-to-end, reproducible deep-learning pipeline applied to
  an Australian conservation problem.
- Engagement with Australian biodiversity infrastructure
  (ALA, GBIF, Darwin Core, EPBC Act listings, IOC taxonomy).
- A documented commitment to participatory design with a
  marginalised community (Deaf citizens scientists, via the
  AUSLAN consultation protocol).
- The kind of artefacts examiners expect of a Master's-level
  research project: datasheet, model card, formal methodology
  document, automated tests, bootstrap CIs, calibration
  analysis, family-level error analysis, YOLO-assisted detection,
  Grad-CAM
  interpretability, and a six-chapter thesis package.

---

## Potential research directions

Several extensions are within the time and scope of a one-to-two
year MPhil:

- **Stronger detector-assisted identification.** Fine-tune YOLO
  on Australian raptor boxes instead of relying on COCO bird
  detections, then quantify whether crop-first classification
  improves difficult flight and multi-bird scenes.
- **Acoustic fusion.** Combine the visual model with raptor
  vocalisation classification (e.g. BirdNET embeddings) for
  multi-modal field surveys.
- **Population-level inference.** Integrate model outputs with
  ALA spatial layers to produce occupancy and detection-probability
  surfaces consistent with the methods of Guillera-Arroita
  et al. (2014).
- **Sub-species disambiguation.** Targeted data collection for
  *Aquila audax fleayi* and other geographically structured
  sub-species, with spatial features as auxiliary input.
- **Domain adaptation across continents.** Compare with the
  author's prior Mexican raptor dataset (53 species, Veracruz)
  to test transfer learning between bird communities.
- **Participatory AUSLAN validation** as a paired computer-
  science + linguistics study, partnering with Macquarie
  University's Auslan Signbank or the Deaf Society NSW.

---

## Future expansion to more Australian raptor species

The roadmap in [`docs/SPECIES_ROADMAP.md`](docs/SPECIES_ROADMAP.md)
sets out three milestones beyond the current eight-species model:

- **v2.0 — 14 species** (adds *Falco berigora*, *Haliaeetus
  leucogaster*, *Haliastur indus*, *H. sphenurus*, *Milvus
  migrans*, *Tachyspiza novaehollandiae*). This will reuse the
  YOLO + EfficientNetB4 pipeline and publish a new model card only
  after the 14-species checkpoint is trained and evaluated.
- **v3.0 — ~20 species** including northern Australian taxa
  (*Aviceda subcristata*, *Macheiramphus alcinus*, *Erythrotriorchis
  radiatus*).
- **v4.0 — all 24 diurnal Australian raptors** (target).

Each tier triggers a new datasheet revision, a model card update,
and a thesis-chapter contribution note.

---

## AUSLAN — explicitly provisional

> The sign vocabulary in this repository is **provisional and
> illustrative**. The animations are programmatically generated
> schematic SVGs that visualise a *proposed* sign motion. They
> are **not** validated AUSLAN.
>
> **No sign in this repository can be considered authoritative
> AUSLAN until it has been validated participatorily with members
> of the Australian Deaf community.** Every species page in the
> web app banners its sign card with
> "PROVISIONAL ILLUSTRATION — pending Deaf community validation".
>
> The full participatory validation protocol — consent forms,
> recommended Deaf-community partners, indicative budget,
> Macquarie Auslan Signbank contacts — is documented in
> [`docs/auslan_consultation/`](docs/auslan_consultation/).

---

## Quick start

### Requirements

- Python 3.13
- ~6 GB free disk for training data (downloaded automatically)
- ~200 MB for the trained model weights
- Optional but recommended for retraining: NVIDIA GPU supported through the official PyTorch CUDA 13.0 build

### Install

```powershell
cd E:\Projects\raptor_australia
python -m venv .venv-modern
.\.venv-modern\Scripts\activate
$env:TEMP = "E:\Projects\raptor_australia\.tmp-pip"
$env:TMP = "E:\Projects\raptor_australia\.tmp-pip"
python -m pip install --upgrade pip setuptools wheel
pip install --no-cache-dir -r requirements.txt
```

Conda remains supported through `environment.yml`, but the direct modern setup used for this compatibility update is the local `.venv-modern` environment on `E:`.

### Verify the install

```bash
python notebooks/run_tests.py
python notebooks/healthcheck.py
```

`run_tests.py` executes pytest with a Windows-safe temporary
directory. `healthcheck.py` then runs syntax, JSON, release-sync,
YOLO-wrapper, template, YAML and pytest checks. It should print
`All checks passed — project is presentable.`

### Build the dataset (skip if you already have one)

```bash
python notebooks/download_ala_images.py            # all species
python notebooks/download_ala_images.py --species aquila_audax
python notebooks/filter_ala_quality.py --use-detector
```

### Train the model

```bash
# EfficientNetB4 is the only v1.5 classifier architecture.
python notebooks/retrain.py --arch efficientnet_b4 --batch-size 4
```

The run writes `models/best_model.pth`,
`results/reporte_final.json`, `results/test_report.csv` and
`results/test_predictions.csv`.

### Run the web app

```bash
cd gui
python app.py
# open http://localhost:5000
```

### Generate thesis figures and metric files

```bash
python notebooks/gradcam_mosaic.py
python notebooks/export_test_predictions.py
python notebooks/bootstrap_metrics.py --report-md
python notebooks/error_analysis.py
python notebooks/calibration_ece.py
```

### Convenience launchers

```bash
# Linux / macOS
./scripts/setup.sh        # one-shot env install
./scripts/run.sh          # launches Flask after sanity-checks

# Windows
scripts\run.bat
```

### Docker

```bash
docker build -t raptor-au .
docker run -p 5000:5000 \
    -v "$(pwd)/models:/app/models:ro" \
    raptor-au
```

The image runs gunicorn behind the Flask app on port 5000 and
expects `models/best_model_efficientnet_b4.pth` (or the legacy
`best_model.pth`) at the mounted volume.

---

## Project structure

```
raptor-australia/
├── README.md, LICENSE, CHANGELOG.md, CITATION.cff
├── RELEASE_MANIFEST_v1_5.md       — release files + SHA-256 hashes
├── requirements.txt, requirements-lock.txt, environment.yml, Dockerfile, .gitignore
│
├── docs/
│   ├── METHODOLOGY.md            — formal Chapter 3 methodology
│   ├── DATASHEET.md              — dataset datasheet (Gebru 2021)
│   ├── MODEL_CARD.md             — model card (Mitchell 2019)
│   ├── THESIS.md                 — formal chapters 1-6 draft
│   ├── Australian_Raptor_Thesis_v1_5.docx — thesis manuscript
│   ├── Australian_Raptor_Thesis_v1_5.pdf  — exported thesis PDF
│   ├── DEFENSE_CHECKLIST.md      — oral defense preparation
│   ├── DEMO_SCRIPT.md            — live demo sequence
│   ├── MASTERS_RESEARCH_PROPOSAL.md — Master's/MPhil proposal
│   ├── MASTERS_PRESENTATION_OUTLINE.md — presentation slide plan
│   ├── SCIENTIFIC_DEFENSIBILITY.md — validity threats + claim boundaries
│   ├── SPLIT_GOVERNANCE.md       — leakage audit and split policy
│   ├── MODEL_REGISTRY.md         — checkpoint hash + class order
│   ├── LIMITATIONS.md            — claims to avoid and validity threats
│   ├── CONTROLLED_DEMO_SET.md    — repeatable demo image set
│   ├── SPECIES_ROADMAP.md        — 8 → 14 → 24 species roadmap
│   ├── TAXONOMY_VERSIONING.md    — IOC reclassification audit
│   ├── SETUP.md                  — step-by-step env setup
│   └── auslan_consultation/      — participatory validation kit
│
├── notebooks/
│   ├── retrain.py                — EfficientNetB4 transfer learning
│   ├── export_test_predictions.py — per-image thesis predictions
│   ├── gradcam.py, gradcam_mosaic.py
│   ├── bootstrap_metrics.py      — 95 % CIs (Efron 1979)
│   ├── error_analysis.py         — family-level confusion
│   ├── calibration_ece.py        — ECE + reliability diagram
│   ├── temperature_scaling.py    — post-hoc calibration
│   ├── build_thesis_docx.py      — reproducible thesis DOCX build
│   ├── audit_thesis_docx.py      — structural DOCX QA fallback
│   ├── export_thesis_pdf.ps1     — Word COM PDF export
│   ├── audit_thesis_pdf.py       — PDF text/metadata audit
│   ├── build_release_manifest.py — SHA-256 release manifest
│   ├── audit_dataset_leakage.py  — duplicate/leakage audit
│   ├── yolo_crop_ablation.py     — YOLO-crop vs whole-image report
│   ├── top3_utility.py           — top-3 citizen-science utility
│   ├── build_model_registry.py   — checkpoint registry entry
│   ├── build_controlled_demo_set.py — presentation demo set
│   ├── fetch_ebird_data.py       — eBird recent-observations
│   ├── download_ala_images.py    — Atlas of Living Australia
│   ├── filter_ala_quality.py     — detector-assisted quality filter
│   ├── generate_auslan_svgs.py   — provisional sign animations
│
├── gui/
│   ├── app.py, yolo_detector.py, species_data.py
│   ├── species_data_i18n.py, i18n.py
│   ├── templates/                — index, species, data, lang picker
│   ├── translations/             — 10-language UI strings
│   └── static/
│       ├── css/, img/species/
│       ├── auslan_videos/        — provisional SVG sign animations
│       └── behavior_videos/      — optional ALA video tiles
│
├── scripts/setup.sh, run.sh, run.bat
│
└── results/
    ├── reporte_final.json        — global + per-species metrics
    ├── test_report.csv           — sklearn classification_report
    ├── test_predictions.csv      — auditable per-image predictions
    ├── bootstrap_ci_efficientnet_b4.* — confidence intervals
    ├── error_analysis_efficientnet_b4.* — family-aware errors
    ├── calibration_efficientnet_b4.json — app-output ECE
    └── yolo_crop_ablation.*      — YOLO crop policy evidence
```

---

## How to cite

```bibtex
@software{fernandez_raptor_au_2026,
  author    = {Fernández-Báez, Brian},
  title     = {Australian Raptor CNN + AUSLAN: Deep learning
               identification of Australian birds of prey with
               provisional sign-language vocabulary},
  year      = {2026},
  url       = {https://github.com/ZOMBIECRAFTIAN/raptor-australia},
  license   = {MIT},
  note      = {Master's-level research prototype prepared for
               prospective Master's by Research / MPhil
               applications in Australia, with a future PhD path.}
}
```

---

## Acknowledgements

- **Atlas of Living Australia** — for the open biodiversity API.
- **iNaturalist Australia** community contributors.
- **Pronatura Veracruz** (Mexico) — the original raptor migration
  context that seeded this project.
- **Auslan Signbank** (Macquarie University) and the **Deaf
  Society of NSW** — listed as prospective consultation partners
  for the participatory AUSLAN validation.

---

## License

MIT — see [`LICENSE`](LICENSE).

Bird image licences are per-image (CC0 / CC-BY / CC-BY-NC),
captured in `dataset/metadata/sources_log.csv` at download time.
The provisional AUSLAN sign illustrations are also MIT-licensed,
but please note the explicit caveat above: they should not be
treated as authoritative AUSLAN.

---

## Contact

**Brian Fernández-Báez** — Computer Systems Engineer (Ingeniero
en Sistemas Computacionales, specialisation in Advanced
Computational Concurrency), Instituto Tecnológico Nacional de
México, Campus Veracruz.

Independent researcher building deep-learning and accessibility
tools for biodiversity, currently preparing Master's by Research
/ MPhil applications in Australia with a future PhD pathway.

For collaboration enquiries — in particular from Deaf-community
partners and Australian raptor researchers — please open a GitHub
Issue on this repository.
