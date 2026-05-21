# Validation Protocol — AUSLAN Sign Vocabulary

This document describes the participatory validation methodology
proposed for the eight raptor signs introduced in
`sign_descriptions.md`. It follows the WFD (World Federation of the
Deaf) ethical guidelines for research involving Deaf participants
and adapts the validation procedure used by Quinto-Pozos & Reynolds
(2012) for scientific sign vocabularies in ASL.

## Phase A — Iterative refinement (2-3 sessions)

**Participants:** 1 Deaf consultant fluent in AUSLAN, 1 hearing
ornithology consultant fluent in AUSLAN, the project
investigator.

**Session 1 (90 min):**
- Present the eight draft signs from `sign_descriptions.md`,
  showing the SVG motion sketches.
- Discuss each sign for cultural and linguistic appropriateness.
- Record proposed modifications.

**Session 2 (60 min):**
- Re-present the revised signs.
- Confirm or further adjust.
- Lock the version that will go to the validation phase.

**Output:** A locked v1.0 of the eight signs, recorded as 15-second
videos performed by the Deaf consultant.

## Phase B — Community validation (single round)

**Participants:** ≥ 12 native AUSLAN signers from the target
community (≥ 6 from NSW/QLD region, ≥ 6 from VIC/TAS/SA region to
capture dialect variation).

**Procedure:** each participant watches the eight v1.0 videos in a
randomised order and rates each sign on three Likert scales
(1 = strongly disagree, 5 = strongly agree):

1. **Clarity** — *"The motion of this sign clearly suggests the
   bird's behaviour or appearance."*
2. **Naturalness** — *"This sign feels like a natural part of
   AUSLAN — it could be used in everyday signing without seeming
   foreign."*
3. **Memorability** — *"After seeing this sign once or twice, I
   could remember and produce it later."*

Optional open-ended comment box per sign for qualitative feedback.

**Acceptance threshold:** A sign passes validation if the **mean
rating across the three scales is ≥ 4.0** with **no scale below
3.5**. Signs that do not pass return to Phase A for one additional
round of refinement.

**Mode of administration:** preferably in-person at a Deaf
community venue (Deaf Society of NSW, RIDBC) or via secure video
call with AUSLAN interpretation if remote. The investigator does
not interpret directly — a registered AUSLAN interpreter handles
all communication during the session.

## Phase C — Production of final video assets

Once validated:

- Record final 8 videos at 1080p, 30 fps, 15 s each, with the same
  consultant for visual consistency.
- Add captioned title (common name + scientific name) at the start.
- Export as `.mp4` (H.264) plus `.webm` (VP9) for browser
  compatibility.
- Place in `gui/static/auslan_videos/<species_key>.mp4` and update
  `app.py SPECIES_INFO[<key>]["auslan_video"] = "<key>.mp4"`.
- Keep the SVG fallbacks for low-bandwidth scenarios.

## Ethics and consent

The protocol assumes one of two ethics frameworks:

**Option 1 — Informal student project (current undergraduate-level
work):** participants sign a plain-language consent form covering
purpose, voluntary participation, anonymity in any published
report, payment of honoraria, and the right to withdraw.

**Option 2 — Formal HREC approval (recommended once enrolled in
MPhil at UQ):** submit the protocol to the UQ Human Research
Ethics Committee. Plan ~6-8 weeks for approval. The Deaf Society
of NSW typically requires HREC approval before referring
participants.

A draft consent form (1 page) is in `consent_form_draft.md` (to be
added once participating organisation specifies their preferred
template).

## Honoraria policy

Recommendation based on Australian academic norms (2024):

- **Deaf consultant (Phase A iterative):** AUD $80/hour.
- **Deaf consultant (Phase C video recording):** AUD $200 per
  recording session (covers up to 2 hours and reuse rights for the
  educational platform).
- **Phase B validation participants:** AUD $50 per participant for
  ~30 min of rating, plus travel reimbursement if applicable.
- **AUSLAN interpreter:** standard NABS rates (~AUD $90/hour, two
  hour minimum).

Total Phase A + B + C budget estimate: see `budget_estimate.md`.

## Acknowledgement statement (for thesis and any publication)

> The AUSLAN sign vocabulary developed in this project was designed
> in consultation with [name(s) of consultant(s)] and validated
> with the participation of [N] members of the [organisation name]
> community. The author thanks [organisation] for their guidance
> and support, without which the inclusive component of this
> project would not have been possible.
>
> Any errors in interpretation or representation remain the sole
> responsibility of the author.

## References

- Quinto-Pozos, D., & Reynolds, W. (2012). ASL discourse strategies:
  Chaining and connecting-explaining across audiences. *Sign
  Language Studies*, 12(2), 211-235.
- World Federation of the Deaf. (2018). *WFD Position Paper on the
  Language Rights of Deaf Children*.
- Pollard, R. Q., et al. (2009). Establishing the reliability of
  the SLPI rating system for ASL fluency. *Sign Language Studies*,
  10(1), 5-32.
