# Taxonomy Versioning — Australian Raptor CNN

This document records the taxonomic authority used by the project,
every reclassification applied since v1.0.0, and the rationale
for each change. Following the precedent established by the
author's prior project (`raptors-cnn`, México) where AOS 2023
reclassifications were documented in
`LISTA_OFICIAL_RAPACES_MEXICO.md`, this file is the equivalent
audit log for the Australian scope.

**Author:** Brian Fernández Báez, Computer Systems Engineer.
**Last update:** 2026-05-12.

---

## 1. Taxonomic authorities followed

The project follows the **International Ornithological Committee
(IOC) World Bird List v14.x** as the primary authority for
binomial nomenclature, supplemented by:

- **BirdLife Australia** (2024) — *Australian Bird Names*
  for common names and Australian taxonomic decisions.
- **Atlas of Living Australia** (ALA) — operational taxonomic
  concept IDs (LSIDs) used for API queries.
- **DAWE / DCCEEW** — EPBC Act 1999 status listings.

When the IOC list and a national authority disagree, the project
documents the conflict explicitly and prefers the national
authority for Australian endemics.

---

## 2. Reclassifications applied (v1.x)

### 2.1 *Accipiter fasciatus* → *Tachyspiza fasciata*

**Status:** ✅ applied in v1.2.0 (April 2026).

**Original placement.** Marchant & Higgins (1993) and Olsen et al.
(1993) classified the Brown Goshawk in genus *Accipiter*.

**Reclassification source.** Catanach et al. (2024), *"Pulling
out the rug: Radical revision of the Accipitridae moves species
across genera"*, Zoological Journal of the Linnean Society,
based on whole-genome phylogenomics. The IOC adopted the
revised genera (Tachyspiza, Astur, Accipiter sensu stricto) in
World Bird List v14.1 (January 2024).

**Practical impact.**
- `SPECIES_INFO[tachyspiza_fasciata]["scientific_name"]` was set
  to *Tachyspiza fasciata*.
- The ALA downloader (`notebooks/download_ala_images.py`) carries
  a synonym map so that `species:"Accipiter fasciatus"` is queried
  as a fallback when the new name returns few records — this is
  essential because ALA's biocache index still holds many records
  under the legacy name.
- 10-language translations (`SPECIES_I18N`) use the new genus
  name; the historical name appears in `did_you_know` as context.

### 2.2 *Falco peregrinus* — explicit subspecies notation

**Status:** ✅ applied in v1.1.0.

The Australian breeding population is the subspecies
*Falco peregrinus macropus* (Swainson 1837). The project's
`scientific_name` field is recorded as *"Falco peregrinus
macropus"* (trinomial), not as the species-level binomial,
because:

1. Australian thesis examiners would expect the trinomial for an
   Australia-only system.
2. ALA records consistently use the trinomial for Australian
   sightings.

### 2.3 *Aquila audax fleayi* — Tasmanian subspecies handling

**Status:** ✅ documented in v1.x.

The Tasmanian subspecies *A. a. fleayi* is listed as Endangered
under EPBC Act 1999 (DAWE 2021), while the continental nominate
*A. a. audax* is not listed at the federal level. The project
keeps a single class `aquila_audax` but the `epbc_status` field
reads *"Not listed (A. a. fleayi: Endangered)"* and the species
profile mentions the subspecific concern explicitly.

If the model is later expanded to subspecies-level
classification (v3.x), Tasmanian birds will be a separate class
with their own ~400 image target.

---

## 3. Reclassifications under consideration (not yet applied)

### 3.1 *Hieraaetus morphnoides* → potential reassignment

Some recent treatments (e.g. del Hoyo et al. 2020 in HBW & BirdLife
International Illustrated Checklist) place this species in
*Aquila* rather than *Hieraaetus*. The IOC list has resisted the
change so far. The project follows IOC pending consensus.

### 3.2 *Circus assimilis* generic placement

No reassignment proposed in the literature as of 2024-2025. Stays
in *Circus* per IOC.

### 3.3 Genus *Accipiter sensu lato* split

The Catanach et al. 2024 paper that moved *fasciatus* to
*Tachyspiza* also moved *novaehollandiae* (Grey Goshawk) to the
same new genus. Pre-emptively recorded for the v2.0 expansion:

| Pre-2024 | Post-2024 (project v2.0) |
|---|---|
| *Accipiter novaehollandiae* | *Tachyspiza novaehollandiae* |
| *Accipiter cirrocephalus* | *Tachyspiza cirrocephala* |

---

## 4. Synonym lookup table (operational)

Used by `notebooks/download_ala_images.py` and
`notebooks/fetch_ebird_data.py` for robust query expansion. When
biocache or eBird return zero records for the current name, the
script automatically retries with each synonym.

```
tachyspiza_fasciata:
  - "Tachyspiza fasciata"         (IOC 2024+)
  - "Accipiter fasciatus"         (legacy; most ALA records)

falco_peregrinus:
  - "Falco peregrinus macropus"   (Australian subspecies)
  - "Falco peregrinus"            (species-level)

aquila_audax:
  - "Aquila audax"                (continental)
  - "Aquila audax fleayi"         (Tasmanian, Endangered)
```

For the v2.0 expansion (14 species), the same scheme will apply
to *Tachyspiza novaehollandiae* / *Accipiter novaehollandiae*.

---

## 5. Process for adding a new reclassification

When a taxonomic change must be applied:

1. Identify the primary source (peer-reviewed paper or IOC
   list update).
2. Add an entry in `§2` of this document with the source citation.
3. Update `SPECIES_INFO[<key>]["scientific_name"]` in `gui/app.py`.
4. Update the 10 locale files in `gui/translations/` if the
   common name changes too.
5. Update `species_data_i18n.py` (`SPECIES_I18N`) likewise.
6. Add the legacy name to the synonym list in the relevant
   downloader (`download_ala_images.py`) so historical records
   are not lost.
7. Note the change in `CHANGELOG.md` under "Changed".
8. Bump the patch version of `CITATION.cff`.

This is the same workflow used for the Veracruz project in its
`AUDITORIA_INCONGRUENCIAS.md`.

---

## 6. References

- Catanach, T. A., et al. (2024). *Pulling out the rug: Radical
  revision of the Accipitridae moves species across genera*.
  Zoological Journal of the Linnean Society.
- Gill, F., D. Donsker, & P. Rasmussen (Eds., 2024). *IOC World
  Bird List v14.x*. https://www.worldbirdnames.org
- Marchant, S., & P. J. Higgins (1993). *HANZAB Vol. 2*.
- Olsen, P., F. Crome, & J. Olsen (1993). *Birds of prey and
  ground birds of Australia*.
- BirdLife Australia (2024). *Australian Bird Names*.
  https://birdlife.org.au
- DAWE (2021). *Australia's Threatened Species Strategy 2021-2026*.
