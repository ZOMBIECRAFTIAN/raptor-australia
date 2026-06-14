# Master's Research Proposal - v1.5 Academic Baseline

## Working Title

YOLO-assisted deep learning for Australian raptor identification under
citizen-science image conditions.

## Degree Fit

This project is scoped as a Master's by Research / MPhil proposal, not
as a completed doctoral thesis. The current repository provides a
validated v1.5 baseline: eight Australian raptor species, a single
EfficientNetB4 classifier, YOLO adaptive localisation, per-image
predictions, bootstrap confidence intervals, calibration analysis,
family-aware error analysis, Darwin Core export, multilingual UI and a
provisional AUSLAN consultation pathway.

The Master's contribution is to turn that prototype into a scientifically
defensible study with stronger experimental controls, clearer uncertainty
reporting and a reproducible research artefact.

## Research Problem

Citizen-science biodiversity platforms can increase ecological monitoring
coverage, but image-based raptor identification is difficult for
non-specialists. A model that is useful for education or triage must be
evaluated not only by accuracy, but also by calibration, class-wise
performance, taxonomy-aware error patterns, data provenance and clear
limits on deployment.

## Aim

To evaluate whether a transparent YOLO-assisted EfficientNetB4 pipeline
can provide a reproducible and scientifically cautious baseline for
Australian raptor identification in citizen-science imagery.

## Research Questions

1. How accurately and reliably can the v1.5 pipeline classify eight
   Australian raptor species on a held-out citizen-science test split?
2. Does YOLO-assisted cropping improve classification robustness compared
   with whole-image inference under the same EfficientNetB4 classifier?
3. Can the system produce auditable biodiversity records and user
   feedback artefacts that are compatible with Darwin Core and future
   dataset improvement?
4. What limitations remain before the system could be used as a stronger
   doctoral-scale ecological AI study?

## Current Evidence

| Item | v1.5 baseline |
|---|---:|
| Active species | 8 |
| Processed images | 1,992 |
| Train / validation / test | 1,590 / 196 / 206 |
| Classifier | EfficientNetB4 |
| Detector/cropper | YOLO |
| Top-1 accuracy | 0.8495 |
| Macro-F1 | 0.8482 |
| Expected calibration error | 0.0639 |
| Family-level accuracy | 0.9272 |

## Proposed Master's Methodology

1. Freeze a reproducible v1.5 baseline with documented class order,
   metrics, per-image predictions and release manifest.
2. Re-run evaluation from `results/test_predictions.csv` using accuracy,
   macro-F1, weighted-F1, per-class F1, bootstrap confidence intervals,
   expected calibration error and taxonomy-aware confusion analysis.
3. Report top-3 accuracy and rescued errors to evaluate citizen-science
   utility beyond top-1 accuracy.
4. Compare whole-image inference against YOLO-cropped inference using the
   same checkpoint and split, reporting the comparison as a controlled
   inference ablation rather than a new architecture claim.
5. Audit dataset risks: licensing, duplicated observations, geographic
   imbalance, photographer/event leakage, age/plumage bias and closed-set
   assumptions.
6. Document Darwin Core export, feedback logging and AUSLAN consultation
   as research infrastructure rather than validated deployment outcomes.

## Deliverables

- Reproducible codebase and CI healthcheck.
- Per-image prediction CSV and statistical reports.
- Dataset datasheet and model card.
- Thesis manuscript in Markdown, DOCX and PDF.
- Scientific defensibility audit.
- Master's presentation/demo script.
- Doctoral continuation roadmap.

## 12-Month Master's Plan

| Month | Milestone |
|---:|---|
| 1-2 | Literature review, ethics/data governance review, baseline freeze. |
| 3-4 | Dataset audit, duplicate/event leakage checks, class-order contract tests. |
| 5-6 | YOLO-crop vs whole-image inference ablation and error analysis. |
| 7-8 | Calibration, bootstrap CIs, taxonomy-aware analysis and model card update. |
| 9-10 | Flask/Darwin Core/feedback reproducibility package and demo evaluation. |
| 11 | Thesis writing, figures, limitations and supervisor review. |
| 12 | Final thesis, presentation and release archive. |

## Boundary Of Claims

The Master's claim is not that the system is production-ready or
state-of-the-art. The defensible claim is narrower: the project provides
a transparent, reproducible and limitation-aware baseline for eight
species, with clear evidence, uncertainty estimates and a credible path
to future doctoral work.

## Bridge To Doctoral Work

A PhD would expand the scientific question from a single validated
baseline to broader ecological AI: 14-24 species, group-aware splits,
raptor-specific YOLO fine-tuning, geographic/domain shift analysis,
active learning and participatory accessibility validation.
