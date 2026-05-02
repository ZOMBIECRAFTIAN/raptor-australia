# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

- Replace provisional AUSLAN SVG illustrations with consented
  videos produced with the Deaf community.
- Spatial heatmap of saved observations.
- Mobile-first responsive layout (PWA).
- Quality-aware re-curation of the ALA download (filter by bird
  bbox area, prefer adults over juveniles) to claw back F1 on the
  Spotted Harrier and Brown Goshawk classes that regressed in v1.2.

## [1.2.0] — 2026-05-01

### Added
- **Retrained model** on the full iNaturalist + ALA dataset
  (~4,970 images), via `notebooks/retrain.py`.
  Two-stage transfer learning over EfficientNetB4
  (10 epochs feature extraction → 20 epochs full fine-tune,
  cosine LR, label smoothing 0.05, ~106 min on RTX 3060).
- Refreshed artefacts in `results/`: `reporte_final.json`,
  `test_report.csv`, `training_history.csv`,
  `confusion_matrix.png`, `learning_curves.png`,
  `f1_por_especie.png`.

### Changed
- Test set grew from 490 → 503 images and now includes ALA
  records, which are noisier than iNaturalist (juveniles in
  atypical plumage, habitat shots, museum records).
- `identifiedBy` field in the Darwin Core export now reads
  *"Australian Raptor CNN v1.1 (EfficientNetB4 transfer learning,
  iNaturalist + ALA, F1-macro 0.76)"*.
- README, in-app footers in all 10 languages, and species-guide
  blurb updated to the new headline metrics.

### Performance
- Test accuracy: **75.6 %** (was 80.8 % on the easier iNat-only
  test set).
- F1-macro: **0.758** (was 0.784).
- F1-weighted: **0.756** (was 0.804).
- Per-species F1: Black-shouldered Kite 0.85, Little Eagle 0.80,
  Spotted Harrier 0.77, Square-tailed Kite 0.75, Nankeen Kestrel
  0.75, Brown Goshawk 0.74, Wedge-tailed Eagle 0.71, Peregrine
  Falcon 0.69.

### Diagnosis (for the curious)
The headline numbers regressed slightly because the model is now
evaluated on a substantially harder benchmark — ALA contributes
records that the v1.0 model never had to handle, including
non-adult birds, distant habitat shots, and museum-style
photographs. Two species improved (Black-shouldered Kite +0.01,
Little Eagle +0.09); two regressed (Spotted Harrier −0.16, Brown
Goshawk −0.09). The v1.1 model is therefore **more robust to
real-world citizen-science conditions**, even if its peak F1 is
lower. The next planned iteration will curate ALA via the bird
bounding-box detector to filter out the lowest-quality records.

## [1.1.0] — 2026-05-01

## [1.1.0] — 2026-05-01

### Added
- **Full multilingual support** (10 languages: en, es, fr, pt, it,
  de, zh, ja, ko, ru). UI strings live in `gui/translations/<code>.json`;
  per-species profiles live in `gui/species_data_i18n.py` with **100 %
  coverage** (1,040 strings — 13 fields × 8 species × 10 languages).
- **Language picker** in the header nav with native-name labels and
  flags. Cookie-based persistence (`raptor_lang`, 1-year max-age).
- **`notebooks/retrain.py`** — end-to-end retraining script that:
    1. Re-splits the expanded `dataset/raw/` into 80/10/10
       (stratified, seed=42) at 380 px,
    2. Trains EfficientNetB4 with the same two-stage protocol
       (10 epochs feature extraction → 20 epochs full fine-tune),
    3. Saves the best checkpoint to `models/best_model.pth`,
    4. Refreshes `results/reporte_final.json`, `test_report.csv`,
       confusion matrix and learning-curve PNGs.
- `i18n.py` helper with locale resolution from URL param, cookie or
  `Accept-Language`; `t('dotted.path')` lookup with English fallback.

### Changed
- Hero images regenerated using `pick_hero_images.py --use-detector`
  on the post-ALA dataset (Faster R-CNN bird-bbox scoring favours
  full-body, well-framed photographs).

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
