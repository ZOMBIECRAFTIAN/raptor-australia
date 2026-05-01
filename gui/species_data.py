"""
Australian Raptor — Detailed species profiles
=========================================================
Merlin Bird ID-style content used by the species catalogue
and the post-identification result panel.

References (consulted during compilation):
  - Marchant, S., & Higgins, P. J. (1993). HANZAB Vol. 2.
  - Olsen, P., Crome, F., & Olsen, J. (1993).
    Birds of prey and ground birds of Australia.
  - Debus, S. (1998). The birds of prey of Australia.
  - DAWE (2021). Threatened Species Strategy 2021–2026.
  - Atlas of Living Australia (2024). Species pages.
  - BirdLife Australia (2024). Species fact sheets.

Each profile follows the same shape so the template can render
all eight species uniformly. Months are spelt with hyphens
("Jul–Nov") to render correctly across browsers.
"""

SPECIES_DETAILS: dict[str, dict] = {
    "aquila_audax": {
        "distribution":
            "Throughout continental Australia, Tasmania, and "
            "southern New Guinea. Occurs from sea level to "
            "alpine zones.",
        "diet":
            "Mammals (rabbits, wallabies, kangaroo joeys, lambs), "
            "reptiles, large birds, and carrion. Frequent "
            "scavenger of roadkill.",
        "behavior":
            "Soars on thermals at great heights, often in pairs. "
            "Highly territorial; pairs hold territories of "
            "30–100 km². Engages in cooperative hunting, with one "
            "bird flushing prey for the other.",
        "migration":
            "Non-migratory and sedentary; territorial pairs occupy "
            "the same range year-round.",
        "nesting":
            "Massive stick nests up to 3 m wide and 2 m deep, in "
            "tall live trees or on cliffs. Same nest reused and "
            "added to over decades.",
        "breeding_months":
            "Apr–Oct (peak Jun–Aug); 1–2 eggs; ~45-day "
            "incubation; fledging at ~80 days.",
        "best_months":
            "Year-round resident; most active on thermals on warm "
            "days, mid-morning to mid-afternoon.",
        "did_you_know":
            "Australia's largest raptor and one of the world's "
            "largest eagles. Can carry prey weighing up to 5 kg — "
            "heavier than its own body. The Tasmanian subspecies "
            "(A. a. fleayi) has fewer than 200 breeding "
            "individuals and is listed as Endangered under the "
            "EPBC Act 1999.",
    },

    "falco_peregrinus": {
        "distribution":
            "Throughout Australia in suitable habitat; concentrated "
            "in coastal cliffs, mountain ranges, and increasingly "
            "in major cities (Sydney, Melbourne, Brisbane).",
        "diet":
            "Almost exclusively birds caught in flight — pigeons, "
            "starlings, parrots, ducks. Occasionally small "
            "mammals.",
        "behavior":
            "Spectacular hunting stoop from height, reaching speeds "
            "over 320 km/h — the fastest sustained motion in the "
            "animal kingdom. Solitary outside the breeding season; "
            "pairs perform aerial display flights during courtship.",
        "migration":
            "Largely sedentary in Australia; northern hemisphere "
            "subspecies are migratory. Australian birds may make "
            "seasonal altitudinal movements.",
        "nesting":
            "Scrapes on cliff ledges, tree hollows, old stick "
            "nests of other species, or — increasingly — ledges "
            "of skyscrapers and bridges.",
        "breeding_months":
            "Jul–Nov; 2–3 eggs; ~32-day incubation; fledging at "
            "38–45 days.",
        "best_months":
            "Year-round resident; most conspicuous during breeding "
            "(Aug–Oct) when pairs are vocal around nest sites.",
        "did_you_know":
            "The fastest animal on Earth — exceeds 320 km/h during "
            "a hunting stoop. Australian populations recovered "
            "strongly after the 1970s DDT ban. Now nests on "
            "bridges and skyscrapers across Australia's major "
            "cities, often on the same building year after year.",
    },

    "circus_assimilis": {
        "distribution":
            "Mainland Australia, mostly inland and northern. Rare "
            "in coastal southeast; absent from Tasmania.",
        "diet":
            "Small mammals (mice, rats, juvenile rabbits), "
            "ground-dwelling birds (especially quails), reptiles, "
            "and large insects.",
        "behavior":
            "Solitary; hunts by gliding low (1–5 m) over open "
            "vegetation in a slow, quartering pattern. Diagnostic "
            "shallow-V dihedral wing posture in flight.",
        "migration":
            "Nomadic; movements driven by prey availability, "
            "particularly rodent irruptions following rains.",
        "nesting":
            "Stick nests in tall isolated paddock trees; the only "
            "Australian harrier that nests above ground. Lays "
            "2–4 eggs.",
        "breeding_months":
            "Spring–summer (Sep–Dec); ~33-day incubation; fledging "
            "at ~36 days.",
        "best_months":
            "Year-round but unpredictable; locally abundant after "
            "rodent plagues in inland regions.",
        "did_you_know":
            "The only member of the Accipitridae (eagles, hawks, "
            "and harriers) with a defined facial disc, similar to "
            "an owl's. The disc focuses the sound of prey moving "
            "in ground vegetation. Listed as Vulnerable in NSW.",
    },

    "tachyspiza_fasciata": {
        "distribution":
            "Throughout Australia including Tasmania, plus New "
            "Guinea and surrounding islands.",
        "diet":
            "Small-to-medium birds, small mammals (especially "
            "rabbits), reptiles, and large insects.",
        "behavior":
            "Ambush hunter — perches in dense canopy then bursts "
            "out in fast pursuit through vegetation. Female "
            "substantially larger than male.",
        "migration":
            "Sedentary; juveniles disperse widely after fledging.",
        "nesting":
            "Stick nests in tall trees in forest, often near "
            "streams. Lays 2–4 eggs.",
        "breeding_months":
            "Spring (Sep–Nov); ~35-day incubation; fledging at "
            "~30 days.",
        "best_months":
            "Year-round, but most visible in spring when "
            "displaying and hunting around nests.",
        "did_you_know":
            "Recently reclassified from Accipiter to the new "
            "genus Tachyspiza in 2024 based on molecular "
            "phylogenetics. Frequently confused with the Grey "
            "Goshawk (T. novaehollandiae), which has a pure-white "
            "form unique to Australia.",
    },

    "falco_cenchroides": {
        "distribution":
            "Throughout Australia, Tasmania, New Guinea, and as "
            "a vagrant to New Zealand.",
        "diet":
            "Insects (especially grasshoppers and beetles), small "
            "mammals, reptiles, and small birds. Highly "
            "opportunistic.",
        "behavior":
            "Distinctive stationary hover, head fixed on a point "
            "while the wings continuously compensate for wind. "
            "Hunts from perches as well as on the wing.",
        "migration":
            "Partially migratory in southern populations — birds "
            "breeding in Tasmania and southern Victoria move "
            "north in autumn, returning in spring. Northern "
            "populations are sedentary.",
        "nesting":
            "Builds no nest; uses tree hollows, cliff ledges, old "
            "corvid nests, or buildings.",
        "breeding_months":
            "Jul–Dec (varies by latitude); 4–5 eggs; ~28-day "
            "incubation.",
        "best_months":
            "Year-round and very common; conspicuous along "
            "roadsides hovering over verges.",
        "did_you_know":
            "The only Australian falcon that hovers systematically. "
            "Often returns to the same roadside lamppost year "
            "after year, hunting over freshly cut grass that "
            "exposes prey. One of the most observed raptors in "
            "Australia thanks to its preference for "
            "human-modified landscapes.",
    },

    "elanus_axillaris": {
        "distribution":
            "Throughout mainland Australia; more abundant in the "
            "southeast and southwest. Vagrant to Tasmania.",
        "diet":
            "Almost exclusively small mammals — predominantly the "
            "introduced house mouse (Mus musculus) and native "
            "rodents. Switches to insects when rodents are "
            "scarce.",
        "behavior":
            "Hovers like a kestrel but with longer wings and a "
            "shorter tail; characteristic 'shoulder-up' posture "
            "during hover. Roosts communally outside the breeding "
            "season.",
        "migration":
            "Highly nomadic and irruptive; populations move long "
            "distances in response to rodent plagues following "
            "rains.",
        "nesting":
            "Stick nest built in the tops of trees in open "
            "country. Lays 3–4 eggs.",
        "breeding_months":
            "Variable, often Aug–Dec but can breed in any month "
            "given a sustained prey supply (e.g. mouse plagues).",
        "best_months":
            "Year-round; locally abundant in years following good "
            "rains when rodents irrupt.",
        "did_you_know":
            "Has striking red eyes and black 'shoulder' patches "
            "contrasted against pure white-grey plumage. Numbers "
            "can increase tenfold during mouse plagues, with "
            "kites concentrating in plague zones from across the "
            "continent.",
    },

    "lophoictinia_isura": {
        "distribution":
            "Northern and eastern Australia, with isolated "
            "populations in Western Australia. Largely absent "
            "from the arid interior.",
        "diet":
            "Specialist nestling-bird predator — takes nestlings, "
            "eggs, large insects (cicadas, stick insects), and "
            "reptiles. Rarely takes mammals.",
        "behavior":
            "Slow, buoyant soaring just above the canopy, "
            "searching for nests. Often follows song-bird alarm "
            "calls to locate breeding pairs.",
        "migration":
            "Partial migrant — southern population (NSW/VIC) "
            "moves north to QLD in autumn and returns in spring; "
            "northern population sedentary.",
        "nesting":
            "Stick nest in tall living eucalypts, typically near "
            "water. Lays 2 eggs.",
        "breeding_months":
            "Aug–Dec; ~40-day incubation; fledging at ~65 days.",
        "best_months":
            "Spring (Sep–Nov) when breeding and most active over "
            "canopies. Partial migrants reach southern Australia "
            "around Aug.",
        "did_you_know":
            "Australia's only canopy-specialist raptor. Listed as "
            "Vulnerable under the EPBC Act with fewer than 1,000 "
            "individuals nationally. Habitat loss in productive "
            "eucalypt forests is the principal threat.",
    },

    "hieraaetus_morphnoides": {
        "distribution":
            "Throughout mainland Australia in suitable habitat; "
            "absent from Tasmania.",
        "diet":
            "Rabbits, small mammals, ground birds, and reptiles. "
            "Takes prey larger than expected for its body size.",
        "behavior":
            "Soars on thermals like a miniature wedge-tailed eagle. "
            "Often confused from below with the whistling kite. "
            "Two distinct plumage morphs (light and dark) "
            "frequently co-occur in the same population.",
        "migration":
            "Partial migrant — birds breeding in southeastern "
            "Australia move north for winter, returning in spring; "
            "northern populations sedentary.",
        "nesting":
            "Large stick nests in tall trees, often on forest "
            "edges. Lays 1–2 eggs.",
        "breeding_months":
            "Jul–Dec (peaks Aug–Oct); ~37-day incubation; "
            "fledging at ~60 days.",
        "best_months":
            "Spring breeding season (Aug–Oct); migrant birds "
            "arrive in southeastern Australia around Jul–Aug.",
        "did_you_know":
            "Australia's smallest eagle. Has declined sharply in "
            "southeastern Australia since the 1980s following "
            "clearing of eucalypt woodland for agriculture. "
            "Currently under monitoring as a threatened species "
            "candidate.",
    },
}
