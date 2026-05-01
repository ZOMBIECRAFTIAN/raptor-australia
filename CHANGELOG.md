# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

- Re-train the model on the expanded ALA + iNaturalist dataset
  (~5,000 images, target F1-macro ≥ 0.85).
- Replace provisional AUSLAN SVG illustrations with consented
  videos produced with the Deaf community.
- Spatial heatmap of saved observations.
- Mobile-first responsive layout (PWA).

## [1.0.0] — 2026-05-01

First public release on GitHub.

### Added
- **Atlas of Living Australia downloader** with synonym-aware
  taxonomy resolution and resumable downloads
  (`notebooks/download_ala_images.py`).
- **Hero image picker** with optional Faster R-CNN bird detection
  for selecting full-body, in-frame catalogue images
  (`notebooks/pick_hero_images.py --use-detector`).
- **AUSLAN sign animation generator** producing 8 SMIL-based SVG
  illustrations of the proposed sign motion patterns
  (`notebooks/generate_auslan_svgs.py`).
- **Detailed species profiles** in Merlin Bird ID style
  (distribution, diet, behaviour, migration, nesting,
  breeding season, best months to observe, did-you-know facts) —
  see `gui/species_data.py`.
- **Per-species model performance pills** (F1 / Precision / Recall)
  on the catalogue cards.
- **`/data` dashboard** with observation stats, per-species
  histogram, and three downloads: internal CSV, **Darwin Core
  CSV** (ALA / GBIF compatible), and feedback log.
- **Consultation package** for AUSLAN community validation
  (`docs/auslan_consultation/`): sign descriptions, email
  template, validation protocol, budget estimate, contacts.
- **Production assets**: Dockerfile, run scripts, GitHub Actions
  CI for syntax verification, CITATION.cff for academic citation.

### Changed
- AUSLAN media now served as `.svg` instead of `.mp4`
  placeholders; `<img>` fallback is rendered when the file is
  missing, with a clearly labelled "provisional" disclaimer.
- `species.html` cards now display training image counts and
  collapsible profile details.

### Fixed
- `/feedback` endpoint always returns JSON, never an HTML error
  page (corrected silent 500 on save).
- Stage and `.gitignore` configured to exclude binary model
  weights (>100 MB GitHub limit) and the ~234 MB raw dataset.

## [0.4.0] — 2026-04 (development snapshot)

### Added
- Flask web application with image-upload identification.
- Top-3 prediction display.
- "Save observation" + "Was this correct?" feedback flow.

### Changed
- EfficientNetB4 backbone selected after benchmarking against
  ResNet-50 (better F1-macro under variable atmospheric
  conditions; see Chen et al., 2021).

## [0.3.0] — 2026-03 (development snapshot)

### Added
- Full training pipeline (`03_training.ipynb`): two-stage
  fine-tuning (10 epochs feature extraction, 20 epochs full).
- Evaluation notebook (`04_evaluation.ipynb`): per-class metrics,
  confusion matrix, learning curves, F1 plot.

### Performance
- Test accuracy: 80.8 %.
- F1-macro: 0.784.
- F1-weighted: 0.804.

## [0.2.0] — 2026-02 (development snapshot)

### Added
- Image preprocessing pipeline: 420×420 resize → 380×380 centre
  crop → ImageNet normalisation.
- Train / validation / test split with seed for reproducibility.

## [0.1.0] — 2026-01 (development snapshot)

### Added
- Initial dataset of ~2,400 images from iNaturalist Australia
  (300 per species across 8 species).
- Project scaffolding and reading list.

[Unreleased]: https://github.com/ZOMBIECRAFTIAN/raptor-australia/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ZOMBIECRAFTIAN/raptor-australia/releases/tag/v1.0.0
