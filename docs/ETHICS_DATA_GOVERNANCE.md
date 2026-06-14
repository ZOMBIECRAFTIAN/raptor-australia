# Ethics And Data Governance

## Intended Use

The system is intended for research, education, demonstration and
citizen-science triage. It is not intended for legal, veterinary,
regulatory or conservation-enforcement decisions.

## Data Sources

The project uses imagery from iNaturalist Australia and the Atlas of
Living Australia. Dataset provenance and licensing limits are documented
in `docs/DATASHEET.md`. The repository contains scripts and derived
artefacts; source image redistribution must respect original licences.

## AI-Assisted Records

Darwin Core exports must be treated as AI-assisted unless reviewed by a
qualified observer. Records should preserve confidence, model version and
observer confirmation status.

## User Risk

The model is closed-set and can confidently misclassify non-raptor or
out-of-scope images. The UI should show uncertainty warnings when
confidence is low or top-2 alternatives are close.

## Accessibility

AUSLAN assets are provisional. They must not be described as validated
AUSLAN signs until reviewed through Deaf-community consultation.

## Bias And Fairness

Citizen-science datasets can reflect camera, location, observer and
species-popularity bias. The v1.5 split is a baseline; stronger
photographer/event-aware split governance is required before stronger
deployment claims.

## Master's Ethics Position

The ethical claim is modest: the project demonstrates transparent
measurement and responsible boundaries. It does not claim automated
authority over biodiversity records.
