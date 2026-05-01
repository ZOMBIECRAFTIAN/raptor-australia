# AUSLAN Consultation Package

This folder contains everything needed to initiate the participatory
validation of the proposed AUSLAN sign vocabulary for the eight
Australian raptor species included in the **Australian Raptor CNN +
AUSLAN** project.

## Why this folder exists

The project's MPhil proposal (University of Queensland) commits to a
*"diseño participativo con comunidades sordas australianas"* in
Chapter 1, §1.3 (Problem 3) and §1.4.3 (Social Justification).
Honouring that commitment requires three concrete steps before any
official sign is published:

1. **Cultural and linguistic review** by Auslan signers fluent in
   the language and familiar with naturalist vocabulary gaps.
2. **Iterative design** of each sign with at least one Deaf
   consultant and one AUSLAN-fluent ornithologist.
3. **Community validation** with measurable criteria (clarity,
   naturalness, memorability) on a sample of ≥ 12 native Auslan
   signers from the target community.

The provisional sign descriptions currently rendered in the GUI
(`gui/static/auslan_videos/*.svg`) are illustrations of the proposed
motion patterns — **not validated AUSLAN signs**. Every screen in
the GUI labels them explicitly as such.

## What's in this folder

| File | Purpose |
|------|---------|
| `sign_descriptions.md` | Formal write-up of each of the 8 proposed signs (motion, hand shape, location, palm orientation, classifier mapping). Ready to share with consultants. |
| `email_template.md` | Editable email to send to the Deaf Society of NSW, RIDBC, or an academic contact. |
| `validation_protocol.md` | Methodology for the validation phase, including consent form outline and acceptance thresholds. |
| `budget_estimate.md` | Indicative budget for honoraria, video production and travel. |
| `contacts.md` | Current contact points (Deaf community organisations + relevant academics). |

## Workflow this package supports

```
Step 1  →  Send email_template.md (adapted) to a Deaf community contact
Step 2  →  Share sign_descriptions.md as the input artefact for review
Step 3  →  Run validation_protocol.md with selected consultants
Step 4  →  Produce 8 short consented videos (~15 s each)
Step 5  →  Replace gui/static/auslan_videos/<species>.svg
            with the consented .mp4 files (same filenames,
            change extension in app.py SPECIES_INFO).
```

## Acknowledgement statement (required for academic publication)

When the validated signs are eventually published, the project's
README and any associated paper must include an Acknowledgement
section attributing the contribution to the named consultants and
the participating Deaf community organisation. A draft is included
at the end of `validation_protocol.md`.
