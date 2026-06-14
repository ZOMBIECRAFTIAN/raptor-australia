# Master's Presentation Outline

## Slide 1 - Title

YOLO-assisted EfficientNetB4 baseline for Australian raptor identification.

## Slide 2 - Research Problem

Citizen-science raptor images are useful but hard to identify reliably.
The project studies whether a transparent computer-vision baseline can
support identification without overstating authority.

## Slide 3 - Dataset

- 1,992 processed images.
- 8 active species.
- Train/validation/test: 1,590 / 196 / 206.
- Sources: iNaturalist Australia and Atlas of Living Australia.

## Slide 4 - Method

- YOLO for bird localisation/cropping.
- EfficientNetB4 for species classification.
- Darwin Core export and feedback logging.
- Provisional AUSLAN consultation pathway.

## Slide 5 - Core Results

- Accuracy: 0.8495.
- Macro-F1: 0.8482.
- Top-3 accuracy: 0.9660.
- Family-level accuracy: 0.9272.

## Slide 6 - Uncertainty And Calibration

- ECE before temperature scaling: 0.0592.
- ECE after temperature scaling: 0.0529.
- NLL changed slightly upward, so calibration benefit is modest.
- Current app-output ECE from `test_predictions.csv`: 0.0639.

## Slide 7 - Leakage And Split Governance

- Exact duplicate groups: 0.
- Source-ID reuse groups: 0.
- Near-duplicate candidates: 13.
- These remain a threat to validity pending visual review and v1.6 split work.

## Slide 8 - YOLO Ablation

- Whole-image accuracy: 0.8495.
- YOLO-crop accuracy: 0.8204.
- Interpretation: YOLO is useful infrastructure, but this checkpoint was
  not trained specifically for crop-only inputs.

## Slide 9 - Demo

Use `docs/CONTROLLED_DEMO_SET.md`:

- 5 easy correct examples.
- 3 difficult examples.
- 2 synthetic out-of-domain examples.

## Slide 10 - Limitations

- Closed-set classifier.
- Generic YOLO detector.
- Possible near-duplicate leakage.
- No validated AUSLAN signs yet.
- Not production or expert replacement.

## Slide 11 - Master's Contribution

The contribution is a reproducible, audited and limitation-aware baseline,
not a final wildlife authority.

## Slide 12 - Future Research Bridge

Future work: group-aware v1.6/v2.0 split, 14+ species, raptor-specific
YOLO fine-tuning, domain shift analysis and participatory accessibility
validation.
