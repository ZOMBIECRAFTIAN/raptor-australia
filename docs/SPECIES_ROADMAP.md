# Species Expansion Roadmap — Australian Raptors

This document tracks the full set of diurnal raptor species native
to or regularly occurring in Australia, the project's coverage
status for each, and the milestones for expanding the CNN to
recognise the complete community rather than only the eight
southeast-Australia subset of v1.x.

Source list:
- Marchant, S., & Higgins, P. J. (Eds.) (1993). *Handbook of
  Australian, New Zealand and Antarctic Birds, Vol. 2*.
- Olsen, P., Crome, F., & Olsen, J. (1993). *Birds of prey and
  ground birds of Australia*.
- Debus, S. (1998). *The birds of prey of Australia: A field guide*.
- BirdLife Australia (2024). *Australian Bird Names*.

## Coverage tiers

- **Tier 1 — v1.x (trained, 8 species)** — included in the current
  EfficientNetB4 classifier (`models/best_model.pth`).
- **Tier 2 — v2.x (next expansion, +6 species)** — diurnal raptors
  with sufficient open-licence image availability on iNaturalist AU
  + Atlas of Living Australia. Will be added to the next training
  cycle.
- **Tier 3 — v3.x (long-term, all remaining species)** — rarer
  diurnal raptors and migratory visitors. Require larger datasets
  and possibly hierarchical classification (family → genus →
  species) to handle the increased class count.

Owls (Strigiformes) are intentionally **out of scope**: they are
nocturnal, ecologically distinct, and would dilute the focus on
diurnal raptors that the MPhil proposal makes.

## Full species list

### 🟢 Tier 1 — included in v1.x (8 species, F1-macro 0.76)

| Family | Scientific name | Common name | EPBC status | Current F1 |
|---|---|---|---|---|
| Accipitridae | *Aquila audax* | Wedge-tailed Eagle | Not listed¹ | 0.71 |
| Accipitridae | *Hieraaetus morphnoides* | Little Eagle | Not listed | 0.80 |
| Accipitridae | *Circus assimilis* | Spotted Harrier | Vulnerable (NSW) | 0.77 |
| Accipitridae | *Tachyspiza fasciata* | Brown Goshawk | Not listed | 0.74 |
| Accipitridae | *Elanus axillaris* | Black-shouldered Kite | Not listed | 0.85 |
| Accipitridae | *Lophoictinia isura* | Square-tailed Kite | **Vulnerable (EPBC Act)** | 0.75 |
| Falconidae | *Falco peregrinus macropus* | Peregrine Falcon | Not listed | 0.69 |
| Falconidae | *Falco cenchroides* | Nankeen Kestrel | Not listed | 0.75 |

¹ Tasmanian subspecies *A. a. fleayi* is Endangered under EPBC Act 1999.

### 🟡 Tier 2 — planned for v2.0 (+6 species)

These have abundant image records in iNaturalist AU and ALA and are
the next logical expansion. After running the data downloaders for
them and a single retraining cycle, the model will cover **14
species**.

| Family | Scientific name | Common name | EPBC status |
|---|---|---|---|
| Accipitridae | *Haliaeetus leucogaster* | White-bellied Sea-Eagle | Vulnerable (NSW, VIC, SA, TAS) |
| Accipitridae | *Milvus migrans* | Black Kite | Not listed |
| Accipitridae | *Haliastur indus* | Brahminy Kite | Not listed |
| Accipitridae | *Haliastur sphenurus* | Whistling Kite | Not listed |
| Accipitridae | *Tachyspiza novaehollandiae* | Grey Goshawk | Vulnerable (TAS, VIC) |
| Falconidae | *Falco berigora* | Brown Falcon | Not listed |

### 🔵 Tier 3 — long-term, all remaining diurnal species (+10 species)

| Family | Scientific name | Common name | EPBC status |
|---|---|---|---|
| Accipitridae | *Pandion cristatus* | Eastern Osprey | Not listed |
| Accipitridae | *Aviceda subcristata* | Pacific Baza | Not listed |
| Accipitridae | *Erythrotriorchis radiatus* | Red Goshawk | **Endangered (EPBC Act)** |
| Accipitridae | *Tachyspiza cirrocephala* | Collared Sparrowhawk | Not listed |
| Accipitridae | *Circus approximans* | Swamp Harrier | Not listed |
| Falconidae | *Falco subniger* | Black Falcon | Vulnerable (NSW) |
| Falconidae | *Falco hypoleucos* | Grey Falcon | **Vulnerable (EPBC Act)** |
| Falconidae | *Falco longipennis* | Australian Hobby | Not listed |

Plus migratory / accidental visitors documented but rarer:
- *Pernis ptilorhynchus* — Crested Honey-buzzard (occasional NT)
- *Spizaetus cirrhatus* — Changeable Hawk-eagle (vagrant Christmas Is.)

### 🤖 Tier 0 — "other" rejection class (in development)

A 9th class targeting non-target birds and out-of-Australia raptors
(e.g. *Elanoides forficatus*, *Cathartes aura*, etc.). Lets the
model say "I don't know" instead of forcing an incorrect Top-1 from
the eight known classes. Detection mechanism for this is already
plumbed at the UI level in v1.3.0 via the *"Other — not one of the
8 trained species"* feedback option, which logs out-of-domain
reports to `results/out_of_domain_log.csv`.

## Milestones for the expansion

### v2.0 — 14-species coverage

1. **Dataset growth.** Run `download_ala_images.py` and the
   iNaturalist scraper with the six Tier-2 scientific names added
   to the `SPECIES_MAP`. Target: ≥ 400 images per species after
   quality filtering.
2. **Quality curation.** Apply `filter_ala_quality.py --use-detector`
   to the expanded raw set.
3. **Re-architect output layer.** Update
   `gui/app.py:AustralianRaptorCNN(num_classes=8)` → `num_classes=14`,
   and add the six new species to `SPECIES_INFO`, `CLASS_ORDER`,
   `species_data_i18n.py` (all 10 languages).
4. **Retrain.** `python notebooks/retrain.py`. Expected F1-macro
   in the 0.72-0.78 range with 14 classes — slightly lower than v1.x
   because of the added confusion pairs, but covering twice as many
   species.
5. **Update artefacts:** README, CHANGELOG, CITATION.cff (bump to
   v2.0.0), per-species hero images, AUSLAN sign descriptions for
   the 6 new species (provisional, with the same disclaimers).

### v3.0 — full Australian diurnal raptor community (~24 species)

1. **Hierarchical classification.** When the class count exceeds
   ~18, flat softmax struggles. Move to a two-stage model:
       - Stage A: family head (Accipitridae / Falconidae /
         Pandionidae).
       - Stage B: per-family species head.
   This matches Merlin Bird ID's own approach for large bird
   communities and is reported in Van Horn et al. (2021)
   *"Benchmarking Representation Learning for Natural World Image
   Collections"*.
2. **OOD via energy scores.** Replace the v1.3 confidence-tier
   heuristic with a principled OOD detector (Liu et al., 2020,
   *Energy-based Out-of-distribution Detection*).
3. **Behaviour-aware identification (research extension).**
   Multi-task head predicting (a) species, (b) flight style
   (soaring / flap-glide / hovering / perched), (c) age class
   (juvenile / adult). Lets the model leverage behavioural context
   the same way Merlin's Step Wizard does.

### v4.0 — beyond Australia (research-grade)

Open-vocabulary classifier built on CLIP or DINOv2, taxonomically
constrained to Accipitriformes + Falconiformes globally. Allows
identification of any raptor worldwide with text-based class
descriptions instead of a fixed softmax. This is realistic only at
PhD-thesis scale.

## How to contribute a new species to the dataset (Tier 2 onwards)

1. Open an issue in the GitHub repo specifying the scientific
   name and your target image count.
2. Run, from the project root:
   ```
   python notebooks/download_ala_images.py --species <new_key>
   ```
   (you will need to extend the `SPECIES_MAP` first in the script.)
3. Inspect the downloaded folder visually; remove obvious junk.
4. Open a pull request adding the new species to `SPECIES_INFO`,
   `CLASS_ORDER`, `species_data_i18n.py`, and a hero JPG.
5. The maintainer will trigger a retraining cycle when at least 3
   new species have been queued.

## How this roadmap maps to the MPhil thesis

The thesis can be presented as a **staged research programme**:

- **Year 1 (current MPhil work):** v1.x — 8 species, EfficientNetB4
  transfer learning, prove the feedback-loop + AUSLAN-inclusion
  methodology works.
- **Year 2 (proposed extension):** v2.x → v3.x — full Australian
  raptor community, hierarchical architecture, energy-based OOD,
  validated AUSLAN videos.
- **Post-thesis:** v4.x — global raptor identification with
  open-vocabulary VLMs as a PhD continuation.

This phased approach is exactly the kind of "research programme
beyond the thesis itself" that admissions committees at UQ
explicitly look for.
