# Scientific Defensibility Audit - v1.5

## Defensible Claim

The project is scientifically defensible as a Master's-level research
prototype if framed as follows:

> A reproducible v1.5 baseline for eight Australian raptor species using
> YOLO-assisted localisation and an EfficientNetB4 classifier, evaluated
> with per-image predictions, bootstrap confidence intervals, calibration,
> family-aware error analysis and explicit limitations.

## Claims To Avoid

- Do not claim production readiness.
- Do not claim expert replacement.
- Do not claim legal, veterinary or conservation-enforcement suitability.
- Do not claim validated AUSLAN signs.
- Do not claim 14-species model performance for the v1.5 checkpoint.
- Do not claim multi-model benchmarking results; the v1.5/v2.0 line is
  EfficientNetB4 + YOLO unless a future supervised study changes scope.

## Evidence Already Present

| Evidence | File |
|---|---|
| Class order contract | `gui/app.py`, `tests/test_project_integrity.py` |
| Per-image predictions | `results/test_predictions.csv` |
| Global metrics | `results/reporte_final.json` |
| Bootstrap CIs | `results/bootstrap_ci_efficientnet_b4.md` |
| Calibration | `results/calibration_efficientnet_b4.json` |
| Family-aware errors | `results/error_analysis_efficientnet_b4.md` |
| Model card | `docs/MODEL_CARD.md` |
| Dataset datasheet | `docs/DATASHEET.md` |
| Release manifest | `RELEASE_MANIFEST_v1_5.md` |
| Thesis PDF audit | `results/thesis_pdf_audit.json` |
| Leakage audit | `results/leakage_audit.md` |
| Top-3 utility | `results/top3_utility.md` |
| Calibration before/after | `results/temperature_scaling_efficientnet_b4.json` |
| Model registry | `docs/MODEL_REGISTRY.md` |
| Controlled demo set | `docs/CONTROLLED_DEMO_SET.md` |

## Threats To Validity

### Internal Validity

- Possible near-duplicate observations across splits. The v1.5 leakage
  audit found no exact duplicate groups and no source-ID reuse, but did
  flag 13 near-duplicate candidate pairs for visual review.
- Per-image split may not control for photographer, location or event.
- YOLO cropping can change the input distribution relative to training
  images if training used whole images.
- Current YOLO detector is generic, not fine-tuned on raptor boxes.

Mitigation for Master's: add duplicate/event leakage audit, report
YOLO-crop versus whole-image inference as an ablation, and avoid
overstating detector-specific gains.

### External Validity

- Citizen-science images may overrepresent accessible locations,
  charismatic species, adult plumage and high-quality cameras.
- Remote Australian regions and juvenile/immature plumages may be
  underrepresented.
- The model is closed-set: it must choose one of eight species even when
  the true species is outside scope.

Mitigation for Master's: document sampling bias, keep out-of-domain
feedback visible, and evaluate v2.0 expansion separately.

### Construct Validity

- Top-1 accuracy alone is not enough for ecological usefulness.
- Confidence may be miscalibrated.
- Species-level errors are not all equally severe; cross-family errors
  are more biologically meaningful than within-family confusions.

Mitigation for Master's: report macro-F1, calibration error, top-3
alternatives and family-aware confusion.

### Ethical And Accessibility Validity

- AUSLAN illustrations are provisional and not community-validated.
- AI-assisted identification can create false confidence for users.
- Image licensing and attribution must remain auditable.

Mitigation for Master's: keep AUSLAN as consultation protocol, not
validated vocabulary; keep model-card warnings prominent; preserve
datasheet provenance.

## Minimum Scientific Standard For Submission

Before using the project in a Master's application or thesis submission:

1. `python notebooks/healthcheck.py --verbose` must pass.
2. `results/test_predictions.csv` must match the active `CLASS_ORDER`.
3. Dataset, model card and methodology must state eight active species.
4. Claims must use accuracy 0.8495 and macro-F1 0.8482 unless a new
   evaluation artefact is generated.
5. Any v2.0 or 14-species statement must be labelled as future work.
6. Any AUSLAN statement must remain provisional pending community review.

## Best Examiner Framing

The strongest Master's defence is not "the app is finished." It is:

> The project is a transparent baseline with unusually strong
> reproducibility artefacts for a student-level prototype, and its limits
> are explicit enough to become a rigorous Master's study.
