# 🦅 Australian Raptor CNN + AUSLAN

> Deep-learning identification of southeast-Australian birds of prey,
> coupled with an inclusive AUSLAN sign-language vocabulary for Deaf
> citizen scientists. Built as the foundation of an MPhil research
> proposal at the **University of Queensland**.

[![CI](https://github.com/ZOMBIECRAFTIAN/raptor-australia/actions/workflows/ci.yml/badge.svg)](https://github.com/ZOMBIECRAFTIAN/raptor-australia/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch 2.x](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg)](https://pytorch.org/)
[![F1-macro 0.76](https://img.shields.io/badge/F1--macro-0.76-yellow.svg)](results/reporte_final.json)
[![Accuracy 75.6%](https://img.shields.io/badge/accuracy-75.6%25-yellowgreen.svg)](results/reporte_final.json)
[![Cite this](https://img.shields.io/badge/cite-CITATION.cff-informational.svg)](CITATION.cff)
[![Status: research preview](https://img.shields.io/badge/status-research%20preview-orange.svg)]()

---

## Why this project exists

Australia experienced its largest documented ecological disaster
during the **Black Summer bushfires (2019–2020)**: an estimated
3 billion vertebrates were affected and 18.6 million hectares burnt
(Ward et al., *Nature Ecology & Evolution* 2020). Recovery monitoring
of apex predators like raptors is a national research priority
(DAWE, 2021), but current methods are slow, manual, and exclude
people with hearing disability from participating in citizen science.

This project addresses three intertwined gaps:

1. **Automation** — a CNN that identifies eight key raptor species
   from in-flight or perched photographs.
2. **Inclusion** — a proposed AUSLAN vocabulary for the species,
   designed participatorily for the ~3.6 M Australians with hearing
   loss (Hearing Australia, 2022).
3. **Interoperability** — every observation can be exported in
   **Darwin Core** format, ready for upload to the Atlas of Living
   Australia or any GBIF data publisher.

A more detailed scientific framing is in
[`docs/auslan_consultation/`](docs/auslan_consultation/) and in the
project's MPhil proposal (available on request).

---

## Target species

Eight raptors of southeast Australia were chosen for ecological
relevance and image availability:

| Common name | Scientific name | EPBC status | F1 (test) |
|---|---|---|---|
| Wedge-tailed Eagle | *Aquila audax* | Not listed (A.a.fleayi: Endangered) | 0.71 |
| Peregrine Falcon | *Falco peregrinus macropus* | Not listed | 0.69 |
| Spotted Harrier | *Circus assimilis* | Vulnerable (NSW) | 0.77 |
| Brown Goshawk | *Tachyspiza fasciata* | Not listed | 0.74 |
| Nankeen Kestrel | *Falco cenchroides* | Not listed | 0.75 |
| Black-shouldered Kite | *Elanus axillaris* | Not listed | 0.85 |
| Square-tailed Kite | *Lophoictinia isura* | **Vulnerable (EPBC Act)** | 0.75 |
| Little Eagle | *Hieraaetus morphnoides* | Not listed | 0.80 |

Per-species precision/recall and confusion matrix are in
[`results/`](results/).

---

## Quick start

### Requirements
- Python 3.10 or newer
- ~6 GB free disk for training data (downloaded automatically)
- ~200 MB for the trained model weights
- Optional but recommended: NVIDIA GPU with CUDA 11.8+

### Install
```bash
# Clone
git clone https://github.com/ZOMBIECRAFTIAN/raptor-australia.git
cd raptor-australia

# Create a Python environment (conda recommended)
conda create -n raptor_env python=3.10 -y
conda activate raptor_env

# Install dependencies
pip install -r requirements.txt
```

### Build the dataset (skip if you already have one)
```bash
# 2,400+ images from the Atlas of Living Australia (no API key)
python notebooks/download_ala_images.py
```
The original iNaturalist scraper used during development is in
`notebooks/01_download_dataset.ipynb`.

### Train the model (or download pre-trained weights)
The training notebook (`notebooks/03_training.ipynb`) reproduces the
EfficientNetB4 fine-tuning end to end. Pre-trained weights
(`models/best_model.pth`, ~185 MB) are not stored in git due to
GitHub's file-size limit; contact the author if you need them or
re-train via the notebook (~1 hour on an RTX 3060).

### Run the web app
```bash
cd gui
python app.py
```
Open <http://localhost:5000>.

### Convenience launchers
```bash
# Linux / macOS
./scripts/setup.sh        # one-shot env install
./scripts/run.sh          # launches Flask after sanity-checks

# Windows
scripts\run.bat           # same, native cmd
```

### Run with Docker
```bash
# Build (excludes dataset and model — image stays small)
docker build -t raptor-au .

# Run, mounting the model from the host
docker run -p 5000:5000 \
    -v "$(pwd)/models:/app/models:ro" \
    raptor-au
```
The image runs gunicorn behind the Flask app on port 5000 and
expects `models/best_model.pth` to be available via the volume
mount. See the `Dockerfile` for details.

---

## What the app does

### `/` — Identify
Upload a photo. The CNN returns:
- Top-1 species + confidence
- Top-3 ranked candidates with confidence bars
- Species fact panel (habitat, status, diagnostic)
- Animated **AUSLAN sign motion** (provisional SVG)
- "Was this correct?" feedback button — corrections feed back into
  the next training cycle.

### `/species` — Species Guide
Card grid of all eight species with:
- Hero image (full-body, automatically picked from the dataset)
- Quick stats (EPBC, length, wingspan)
- Field diagnostic
- Detailed species profile (Merlin-Bird-ID style: distribution,
  diet, behaviour, migration, nesting, breeding season,
  best months to observe, did-you-know fact)
- AUSLAN sign description
- Per-class model performance (F1 / Precision / Recall)
- Training image count

### `/data` — Data dashboard & export
- Live stats (observations · species recorded · model corrections)
- Histogram of observations per species
- Three downloads:
  - Internal CSV (your raw observations)
  - **Darwin Core CSV** — ready to upload to the
    [Atlas of Living Australia](https://www.ala.org.au) or any
    GBIF publisher
  - Feedback log — input for the next retraining cycle

---

## Architecture

```
Input image (JPG/PNG/TIFF/WebP, ≤ 16 MB)
        │
        ▼
┌──────────────────────────┐
│  Pre-processing           │  Resize 420 → CenterCrop 380
│  ImageNet normalisation   │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│  EfficientNetB4 backbone  │  Pre-trained on ImageNet (1.2 M images)
│  (frozen during stage 1)  │
├──────────────────────────┤
│  Custom classifier head    │  Dropout(0.4) + Linear(1792→512)
│  (8 species output)        │  + ReLU + Dropout(0.2) + Linear(512→8)
└──────────────────────────┘
        │
        ▼
   Softmax probabilities  ─►  Top-3 species + confidences
                              + species fact panel
                              + AUSLAN sign motion
```

**Why EfficientNetB4?** Best precision/efficiency trade-off in our
benchmarks for in-flight bird classification. Compared with ResNet-50
(83.0% top-1 ImageNet) it delivers comparable accuracy with fewer
parameters (19 M vs. 25 M), is small enough for CPU inference, and
the 380-px input matches the typical resolution of citizen-science
photos (Tan & Le, *ICML* 2019; Chen et al., 2021).

---

## Project structure

```
raptor-australia/
├── README.md, LICENSE, requirements.txt, .gitignore
│
├── dataset/                    (mostly excluded from git — too large)
│   ├── raw/                    — ~5,000 source images, 8 species
│   ├── processed/              — train/val/test splits (380 px)
│   ├── metadata/               — per-species CSV logs ✅ in git
│   └── feedback/               — user-submitted corrections
│
├── models/
│   └── best_model.pth          (185 MB — excluded from git)
│
├── notebooks/
│   ├── 01_download_dataset.ipynb       — iNaturalist scraper
│   ├── 02_preprocessing.ipynb          — resize, augment, split
│   ├── 03_training.ipynb               — EfficientNetB4 fine-tuning
│   ├── 04_evaluation.ipynb             — metrics + confusion matrix
│   ├── download_ala_images.py          — Atlas of Living Australia
│   ├── pick_hero_images.py             — quality-aware hero picker
│   └── generate_auslan_svgs.py         — sign animation generator
│
├── gui/
│   ├── app.py                  — Flask backend, model serving, exports
│   ├── species_data.py         — Merlin-style species profiles
│   ├── templates/              — index.html, species.html, data.html
│   └── static/
│       ├── css/style.css       — full UI stylesheet
│       ├── img/species/        — 8 hero JPGs (auto-picked)
│       └── auslan_videos/      — 8 SVG sign animations
│
├── docs/
│   └── auslan_consultation/
│       ├── README.md, sign_descriptions.md
│       ├── email_template.md, validation_protocol.md
│       ├── budget_estimate.md, contacts.md
│
└── results/
    ├── reporte_final.json      — global + per-species metrics
    ├── test_report.csv         — sklearn classification_report
    ├── training_history.csv    — loss/accuracy per epoch
    └── *.png                   — confusion matrix, learning curves, F1 chart
```

---

## Performance

Final test set: **490 images held out** during training (no leakage).

| Metric | Value |
|---|---|
| Accuracy | **75.6 %** |
| F1-macro | **0.758** |
| F1-weighted | 0.756 |
| Architecture | EfficientNetB4 (transfer learning) |
| Training images | ~3,975 (80 % split, +augmentation) |
| Val / Test images | 497 / 503 |
| Training time | ~106 min on RTX 3060 |

> **A note on the metric drop vs. v1.0.0.** The original model
> trained only on iNaturalist Australia (~2,400 images) reached
> F1-macro 0.78 on its own iNat-style test set. Retraining on
> the *expanded* iNaturalist + Atlas of Living Australia dataset
> (~5,000 images) brought F1-macro down to 0.76 — but this is
> evaluated on a substantially **harder** test set that includes
> habitat shots, juveniles in atypical plumage, and museum-record
> photographs that the iNat-only model never had to handle. The
> v1.1 model is therefore **more robust to real-world citizen
> science conditions**, even if its headline F1 is slightly
> lower than the v1.0 number. Per-species results show
> Black-shouldered Kite and Little Eagle improved with the
> larger dataset, while Spotted Harrier and Brown Goshawk
> dropped because ALA contributes more juvenile records for
> those species, which the model now needs to learn to handle.

Per-class performance and learning curves are visualised in
[`results/`](results/).

---

## Re-deriving the catalogue hero images

After downloading the Atlas of Living Australia images
(`download_ala_images.py`), regenerate the catalogue thumbnails
with quality-aware bird detection:

```bash
python notebooks/pick_hero_images.py --use-detector --apply
```

The picker scores every candidate image with sharpness, resolution
and a Faster R-CNN bird-bounding-box criterion (full-body shots
score highest). Output:
- `gui/static/img/species/<species>.jpg` — the picked hero
- `results/hero_candidates_<species>.jpg` — top-6 contact sheet
- `results/hero_scores.csv` — full ranking table

---

## AUSLAN consultation

The sign vocabulary in this project is **provisional**. Every screen
labels it as such. The full participatory validation methodology —
including draft consent forms, recommended Deaf community contacts,
and a budget — is in
[`docs/auslan_consultation/`](docs/auslan_consultation/).

Validation is required before any sign in this repository can be
considered authoritative AUSLAN.

---

## How to cite

```bibtex
@software{fernandez_raptor_au_2026,
  author    = {Fernández Báez, Brian},
  title     = {Australian Raptor CNN + AUSLAN: Deep learning
               identification of Australian birds of prey with
               inclusive sign-language vocabulary},
  version   = {1.0},
  year      = {2026},
  url       = {https://github.com/ZOMBIECRAFTIAN/raptor-australia},
  license   = {MIT}
}
```

---

## Roadmap

- [x] Dataset curation (iNaturalist + Atlas of Living Australia)
- [x] EfficientNetB4 fine-tuning v1.0 (iNat-only: Acc 80.8 %, F1 0.78)
- [x] Retraining v1.1 on iNat + ALA dataset (Acc 75.6 %, F1 0.76 — harder benchmark)
- [x] Flask web app with feedback loop
- [x] Species catalogue with Merlin-style profiles
- [x] AUSLAN sign animations (provisional)
- [x] Darwin Core export to ALA / GBIF
- [ ] Validated AUSLAN videos (pending Deaf community consultation)
- [ ] Re-train with feedback corrections (target: F1 ≥ 0.85)
- [ ] Mobile-responsive frontend (PWA)
- [ ] Spatial heatmap of observations

---

## Acknowledgements

- **University of Queensland** — Centre for Biodiversity and
  Conservation Science (CBCS) for inspiring the Australian focus.
- **Atlas of Living Australia** for the open biodiversity API.
- **iNaturalist Australia** community contributors.
- **Pronatura Veracruz** (Mexico) — original raptor migration
  context that seeded this project.
- **Deaf Society of NSW** and **Auslan Signbank** (Macquarie
  University) — pending consultation partners.

---

## License

MIT — see [`LICENSE`](LICENSE).

Note that **bird images**, **the AUSLAN vocabulary**, and the
**model weights** have additional terms documented in `LICENSE`.

---

## Contact

**Brian Fernández Báez** — Computer Systems Engineer
(Ingeniero en Sistemas Computacionales, with a specialisation in
Advanced Computational Concurrency), Instituto Tecnológico Nacional
de México — Campus Veracruz. Independent researcher building deep
learning + accessibility tools for biodiversity. MPhil candidate,
University of Queensland (application 2026).

For collaboration enquiries (especially Deaf community partners and
Australian raptor researchers), please open an issue on this
repository or email via the address listed on my GitHu