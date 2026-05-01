# Contributing to Australian Raptor CNN + AUSLAN

Thank you for your interest in contributing. This is an academic
project and the structure of contributions reflects that.

## Ways to contribute

### Reporting issues

Open an issue on
[GitHub](https://github.com/ZOMBIECRAFTIAN/raptor-australia/issues)
for any of:

- Bugs in the Flask application or notebooks.
- Inaccurate species information or scientific naming
  (please cite a primary source for any correction).
- Suggestions for additional Australian raptor species to include.
- Performance regressions after model retraining.

### Contributing data

If you have additional well-curated raptor images that are CC-BY,
CC0, or CC-BY-NC licensed, please open an issue with:
- The species (project key, e.g. `aquila_audax`).
- A link to the image source and licence.
- An estimate of the number of usable images.

Do **not** open a pull request that adds images to the repository
directly — the dataset is intentionally excluded from git for size
reasons (see `.gitignore`).

### Contributing code

Pull requests are welcome for:
- Bug fixes (please reference an open issue).
- Improvements to the export schema (Darwin Core fields).
- New evaluation metrics or visualisations.
- Additional notebook documentation.

Please:
1. Open an issue first to discuss the proposed change.
2. Branch off `main` with a descriptive branch name
   (`fix/feedback-json-response`, `feature/grad-cam-explainer`).
3. Run `python -c "import ast; ast.parse(open('gui/app.py').read())"`
   on any Python file you modify, plus a Jinja render check on
   any template you change.
4. Update `CHANGELOG.md` under "Unreleased".
5. Submit the PR with a clear description of what changed and why.

## What this project does NOT accept

### AUSLAN sign modifications without consultation

The AUSLAN vocabulary in `gui/species_data.py` and
`gui/static/auslan_videos/` is **provisional** and reserved for
community validation. Pull requests that add, modify or "improve"
the sign descriptions or animations will be respectfully closed
unless they come from, or have been approved by, an AUSLAN-fluent
member of the Australian Deaf community via the consultation
protocol in `docs/auslan_consultation/`.

This is a hard rule. The integrity of the inclusive component
depends on it.

### Direct image uploads

The dataset is not stored in git. Use
`notebooks/download_ala_images.py` (no API key) or the iNaturalist
scraper in `01_download_dataset.ipynb` to rebuild it locally.

### Production-grade demands

This is an MPhil research preview, not a maintained product. While
the codebase is organised, performance and security hardening have
not been done at production scale.

## Code of conduct

Contributors and consultants are expected to engage respectfully
with all participants, especially members of the Deaf community
and Indigenous Australian researchers whose input on biodiversity
naming conventions may be sought during validation.

## Acknowledgements

Substantive contributions will be acknowledged in:
- `CHANGELOG.md` under the relevant version.
- The corresponding section of `README.md`.
- Any academic publication that arises from this codebase, in
  accordance with the contributor's preferred name and affiliation.
