# Limitations And Threats To Validity

## Scope

This release is a Master's-level research baseline, not a deployment-ready
wildlife authority. Its strongest contribution is transparent measurement,
not final ecological coverage.

## Dataset Limitations

- The current split is per image. It may not fully control for photographer,
  observation event, location or near-duplicate leakage.
- The v1.5 leakage audit found no exact duplicate or source-ID leakage,
  but it did flag near-duplicate candidates requiring visual review.
- Citizen-science images may overrepresent accessible areas, adult plumage,
  popular species, high-quality cameras and charismatic views.
- The test set has 206 images, which is useful for a baseline but still
  small for strong ecological deployment claims.
- Licensing and provenance are documented, but the dataset itself is not
  redistributed.

## Model Limitations

- The classifier is closed-set: it must choose one of eight species even
  for non-raptor or out-of-scope images.
- YOLO is currently a generic detector/cropper, not a raptor-specific
  detector trained on annotated raptor boxes.
- YOLO cropping can help localisation, but it must be reported with an
  ablation because the classifier was trained on the available processed
  imagery rather than a dedicated crop-only training set.
- Confidence is a softmax score and requires calibration checks before
  user-facing trust claims.

## Evaluation Limitations

- Accuracy and macro-F1 are necessary but not sufficient; top-3 accuracy,
  calibration, family-aware errors and uncertainty should be reported.
- Cross-family confusions are more biologically serious than many
  within-family confusions.
- Grad-CAM visualisations are explanatory aids, not proof of causal model
  reasoning.

## Accessibility And Ethics

- AUSLAN assets are provisional illustrations only. They are not validated
  signs until reviewed with Deaf community participants and interpreters.
- The app should be framed as educational or triage support, not expert
  replacement.
- Darwin Core export records should remain labelled as AI-assisted unless
  reviewed by a qualified observer.

## Master's Defence Position

The defensible Master's claim is:

> This project provides a reproducible, limitation-aware baseline for
> eight Australian raptor species, with real metrics and a clear path to
> stronger doctoral research.

The non-defensible claim is:

> This project is a final production classifier for Australian raptors.
