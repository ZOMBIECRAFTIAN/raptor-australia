"""
Localised species data for the 10 supported languages.

Each language entry has the same 8 species × 13 fields. English
serves as the baseline; missing or empty values in other
languages fall back to English via ``get_species_data()``.

Fields:
    common_name, epbc_status, habitat, diagnostic, auslan_sign,
    distribution, diet, behaviour, migration, nesting,
    breeding_months, best_months, did_you_know.
"""

from __future__ import annotations


# ════════════════════════════════════════════════════════════
# ENGLISH — canonical baseline
# ════════════════════════════════════════════════════════════
_EN = {
    "aquila_audax": {
        "common_name": "Wedge-tailed Eagle",
        "epbc_status": "Not listed (A. a. fleayi: Endangered)",
        "habitat": "Open woodland, scrubland, grassland",
        "diagnostic": "Diamond/wedge-shaped tail, arched wings in soaring flight",
        "auslan_sign": "Both hands in inverted V, extend downward with wide amplitude",
        "distribution": "Throughout continental Australia, Tasmania, and southern New Guinea. Occurs from sea level to alpine zones.",
        "diet": "Mammals (rabbits, wallabies, kangaroo joeys, lambs), reptiles, large birds, and carrion. Frequent scavenger of roadkill.",
        "behaviour": "Soars on thermals at great heights, often in pairs. Highly territorial; pairs hold territories of 30–100 km². Engages in cooperative hunting.",
        "migration": "Non-migratory and sedentary; territorial pairs occupy the same range year-round.",
        "nesting": "Massive stick nests up to 3 m wide and 2 m deep, in tall live trees or on cliffs. Same nest reused for decades.",
        "breeding_months": "Apr–Oct (peak Jun–Aug); 1–2 eggs; ~45-day incubation; fledging at ~80 days.",
        "best_months": "Year-round resident; most active on thermals on warm days, mid-morning to mid-afternoon.",
        "did_you_know": "Australia's largest raptor and one of the world's largest eagles. Can carry prey weighing up to 5 kg — heavier than its own body. The Tasmanian subspecies (A. a. fleayi) has fewer than 200 breeding individuals.",
    },
    "falco_peregrinus": {
        "common_name": "Peregrine Falcon",
        "epbc_status": "Not listed",
        "habitat": "Cliffs, urban areas, coastlines",
        "diagnostic": "Long pointed wings, black malar stripe, fast vertical stoop",
        "auslan_sign": "Dominant hand index finger, rapid vertical dive downward",
        "distribution": "Throughout Australia in suitable habitat; concentrated in coastal cliffs, mountain ranges, and increasingly in major cities.",
        "diet": "Almost exclusively birds caught in flight — pigeons, starlings, parrots, ducks. Occasionally small mammals.",
        "behaviour": "Spectacular hunting stoop from height, reaching speeds over 320 km/h — the fastest sustained motion in the animal kingdom.",
        "migration": "Largely sedentary in Australia; northern hemisphere subspecies are migratory.",
        "nesting": "Scrapes on cliff ledges, tree hollows, old stick nests, or ledges of skyscrapers and bridges.",
        "breeding_months": "Jul–Nov; 2–3 eggs; ~32-day incubation; fledging at 38–45 days.",
        "best_months": "Year-round resident; most conspicuous during breeding (Aug–Oct) when pairs are vocal around nest sites.",
        "did_you_know": "The fastest animal on Earth — exceeds 320 km/h during a hunting stoop. Australian populations recovered after the 1970s DDT ban and now nest on bridges and skyscrapers across the country.",
    },
    "circus_assimilis": {
        "common_name": "Spotted Harrier",
        "epbc_status": "Vulnerable (NSW)",
        "habitat": "Grassland, scrubland, open farmland",
        "diagnostic": "Facial disc, shallow V dihedral, low sweeping flight",
        "auslan_sign": "Both flat hands, lateral oscillating glide at low height",
        "distribution": "Mainland Australia, mostly inland and northern. Rare in coastal southeast; absent from Tasmania.",
        "diet": "Small mammals (mice, rats, juvenile rabbits), ground-dwelling birds (especially quails), reptiles, and large insects.",
        "behaviour": "Solitary; hunts by gliding low (1–5 m) over open vegetation in a slow, quartering pattern. Diagnostic shallow-V dihedral.",
        "migration": "Nomadic; movements driven by prey availability, particularly rodent irruptions following rains.",
        "nesting": "Stick nests in tall isolated paddock trees; the only Australian harrier that nests above ground.",
        "breeding_months": "Spring–summer (Sep–Dec); ~33-day incubation; fledging at ~36 days.",
        "best_months": "Year-round but unpredictable; locally abundant after rodent plagues.",
        "did_you_know": "The only Accipitridae with a defined facial disc, similar to an owl's. The disc focuses sound from prey moving in vegetation. Listed as Vulnerable in NSW.",
    },
    "tachyspiza_fasciata": {
        "common_name": "Brown Goshawk",
        "epbc_status": "Not listed",
        "habitat": "Dense forest, woodland",
        "diagnostic": "Short rounded wings, long banded tail, yellow iris",
        "auslan_sign": "Curved hand, rapid zigzag movement between trees",
        "distribution": "Throughout Australia including Tasmania, plus New Guinea and surrounding islands.",
        "diet": "Small-to-medium birds, small mammals (especially rabbits), reptiles, and large insects.",
        "behaviour": "Ambush hunter — perches in dense canopy then bursts out in fast pursuit. Female substantially larger than male.",
        "migration": "Sedentary; juveniles disperse widely after fledging.",
        "nesting": "Stick nests in tall trees in forest, often near streams. Lays 2–4 eggs.",
        "breeding_months": "Spring (Sep–Nov); ~35-day incubation; fledging at ~30 days.",
        "best_months": "Year-round, but most visible in spring when displaying around nests.",
        "did_you_know": "Reclassified from Accipiter to Tachyspiza in 2024 based on molecular phylogenetics. Frequently confused with the Grey Goshawk, which has a pure-white form unique to Australia.",
    },
    "falco_cenchroides": {
        "common_name": "Nankeen Kestrel",
        "epbc_status": "Not listed",
        "habitat": "Open habitats, grassland, farmland",
        "diagnostic": "Stationary hovering over open ground, rufous coloration, fan tail",
        "auslan_sign": "Open hand, stationary vibration (hovering motion)",
        "distribution": "Throughout Australia, Tasmania, New Guinea, and as a vagrant to New Zealand.",
        "diet": "Insects (especially grasshoppers and beetles), small mammals, reptiles, and small birds.",
        "behaviour": "Distinctive stationary hover, head fixed on a point while wings continuously compensate for wind.",
        "migration": "Partially migratory in southern populations — Tasmanian and Victorian birds move north in autumn.",
        "nesting": "Builds no nest; uses tree hollows, cliff ledges, old corvid nests, or buildings.",
        "breeding_months": "Jul–Dec; 4–5 eggs; ~28-day incubation.",
        "best_months": "Year-round and very common; conspicuous along roadsides hovering over verges.",
        "did_you_know": "The only Australian falcon that hovers systematically. Often returns to the same roadside lamppost year after year. One of the most observed raptors in Australia.",
    },
    "elanus_axillaris": {
        "common_name": "Black-shouldered Kite",
        "epbc_status": "Not listed",
        "habitat": "Grassland, agricultural areas, wetland edges",
        "diagnostic": "Black shoulder patches, white-grey plumage, red iris, hovering",
        "auslan_sign": "Both hands in H, hover then short descent",
        "distribution": "Throughout mainland Australia; more abundant in the southeast and southwest.",
        "diet": "Almost exclusively small mammals — predominantly the introduced house mouse and native rodents.",
        "behaviour": "Hovers like a kestrel but with longer wings; characteristic 'shoulder-up' posture during hover. Roosts communally.",
        "migration": "Highly nomadic and irruptive; populations move long distances in response to rodent plagues.",
        "nesting": "Stick nest built in the tops of trees in open country. Lays 3–4 eggs.",
        "breeding_months": "Variable, often Aug–Dec but can breed any month given a sustained prey supply.",
        "best_months": "Year-round; locally abundant in years following good rains when rodents irrupt.",
        "did_you_know": "Has striking red eyes and black 'shoulder' patches. Numbers can increase tenfold during mouse plagues, with kites concentrating in plague zones from across the continent.",
    },
    "lophoictinia_isura": {
        "common_name": "Square-tailed Kite",
        "epbc_status": "Vulnerable (EPBC Act)",
        "habitat": "Mature eucalyptus forest, woodland",
        "diagnostic": "Long square tail, slow soaring over forest canopy",
        "auslan_sign": "Flat hand, slow glide with square tail demarcated",
        "distribution": "Northern and eastern Australia, with isolated populations in Western Australia.",
        "diet": "Specialist nestling-bird predator — takes nestlings, eggs, large insects, and reptiles.",
        "behaviour": "Slow, buoyant soaring just above the canopy, searching for nests. Often follows song-bird alarm calls.",
        "migration": "Partial migrant — southern population (NSW/VIC) moves north to QLD in autumn and returns in spring.",
        "nesting": "Stick nest in tall living eucalypts, typically near water. Lays 2 eggs.",
        "breeding_months": "Aug–Dec; ~40-day incubation; fledging at ~65 days.",
        "best_months": "Spring (Sep–Nov) when breeding and most active over canopies.",
        "did_you_know": "Australia's only canopy-specialist raptor. Listed as Vulnerable under the EPBC Act with fewer than 1,000 individuals nationally.",
    },
    "hieraaetus_morphnoides": {
        "common_name": "Little Eagle",
        "epbc_status": "Not listed",
        "habitat": "Open woodland, forest edges",
        "diagnostic": "Small size for eagle, broad rounded wings, short tail, small crest",
        "auslan_sign": "Compact hand, small active movement (small size + broad wings)",
        "distribution": "Throughout mainland Australia in suitable habitat; absent from Tasmania.",
        "diet": "Rabbits, small mammals, ground birds, and reptiles. Takes prey larger than expected for its body size.",
        "behaviour": "Soars on thermals like a miniature wedge-tailed eagle. Two distinct plumage morphs (light and dark).",
        "migration": "Partial migrant — birds breeding in southeastern Australia move north for winter.",
        "nesting": "Large stick nests in tall trees, often on forest edges. Lays 1–2 eggs.",
        "breeding_months": "Jul–Dec (peaks Aug–Oct); ~37-day incubation; fledging at ~60 days.",
        "best_months": "Spring breeding season (Aug–Oct); migrant birds arrive in southeastern Australia around Jul–Aug.",
        "did_you_know": "Australia's smallest eagle. Has declined sharply in southeastern Australia since the 1980s following clearing of eucalypt woodland.",
    },
}


# ════════════════════════════════════════════════════════════
# SPANISH
# ════════════════════════════════════════════════════════════
_ES = {
    "aquila_audax": {
        "common_name": "Águila de cola en cuña",
        "epbc_status": "No listada (A. a. fleayi: En peligro)",
        "habitat": "Bosque abierto, matorral, pastizal",
        "diagnostic": "Cola en forma de diamante o cuña, alas arqueadas en planeo",
        "auslan_sign": "Ambas manos en V invertida, extender hacia abajo con amplitud",
        "distribution": "En toda Australia continental, Tasmania y el sur de Nueva Guinea. Se encuentra desde el nivel del mar hasta zonas alpinas.",
        "diet": "Mamíferos (conejos, walabíes, crías de canguro, corderos), reptiles, aves grandes y carroña. Carroñero frecuente.",
        "behaviour": "Planea en térmicas a gran altura, a menudo en pareja. Muy territorial; las parejas mantienen territorios de 30–100 km². Caza cooperativa.",
        "migration": "No migratoria y sedentaria; las parejas territoriales ocupan la misma área todo el año.",
        "nesting": "Nidos enormes de palos de hasta 3 m de ancho, en árboles altos o acantilados. Mismo nido reusado durante décadas.",
        "breeding_months": "Abr–Oct (pico Jun–Ago); 1–2 huevos; ~45 días de incubación; emplumado a los ~80 días.",
        "best_months": "Residente todo el año; más activa en térmicas en días cálidos, de media mañana a media tarde.",
        "did_you_know": "La rapaz más grande de Australia y una de las águilas más grandes del mundo. Puede cargar presas de hasta 5 kg, más pesadas que su propio cuerpo. La subespecie tasmana (A. a. fleayi) tiene menos de 200 individuos reproductivos.",
    },
    "falco_peregrinus": {
        "common_name": "Halcón peregrino",
        "epbc_status": "No listado",
        "habitat": "Acantilados, áreas urbanas, costas",
        "diagnostic": "Alas largas y puntiagudas, bigote negro, picada vertical rápida",
        "auslan_sign": "Dedo índice de la mano dominante, picada vertical rápida hacia abajo",
        "distribution": "En toda Australia en hábitat adecuado; concentrado en acantilados costeros, cordilleras y, cada vez más, en grandes ciudades.",
        "diet": "Casi exclusivamente aves capturadas en vuelo: palomas, estorninos, loros, patos. Ocasionalmente pequeños mamíferos.",
        "behaviour": "Espectacular picada de caza desde altura, alcanzando velocidades superiores a 320 km/h, el movimiento sostenido más rápido del reino animal.",
        "migration": "Mayormente sedentario en Australia; las subespecies del hemisferio norte son migratorias.",
        "nesting": "Pone los huevos en repisas de acantilados, huecos de árboles, nidos viejos de palos, o repisas de rascacielos y puentes.",
        "breeding_months": "Jul–Nov; 2–3 huevos; ~32 días de incubación; emplumado a los 38–45 días.",
        "best_months": "Residente todo el año; más visible durante la cría (Ago–Oct) cuando las parejas vocalizan cerca del nido.",
        "did_you_know": "El animal más rápido del planeta — supera los 320 km/h en su picada de caza. Las poblaciones australianas se recuperaron tras la prohibición del DDT en los 70 y ahora anidan en puentes y rascacielos por todo el país.",
    },
    "circus_assimilis": {
        "common_name": "Aguilucho manchado",
        "epbc_status": "Vulnerable (NSW)",
        "habitat": "Pastizal, matorral, tierras agrícolas abiertas",
        "diagnostic": "Disco facial, V poco profunda en planeo, vuelo rasante",
        "auslan_sign": "Ambas manos planas, planeo lateral oscilante a baja altura",
        "distribution": "Australia continental, principalmente interior y norte. Raro en costa sudeste; ausente en Tasmania.",
        "diet": "Pequeños mamíferos (ratones, ratas, conejos juveniles), aves de suelo (especialmente codornices), reptiles e insectos grandes.",
        "behaviour": "Solitario; caza planeando bajo (1–5 m) sobre vegetación abierta en patrón lento y cuadriculado. V poco profunda diagnóstica.",
        "migration": "Nómada; movimientos según disponibilidad de presas, especialmente irrupciones de roedores tras lluvias.",
        "nesting": "Nidos de palos en árboles altos aislados; el único aguilucho australiano que anida sobre el suelo.",
        "breeding_months": "Primavera-verano (Sep–Dic); ~33 días de incubación; emplumado a los ~36 días.",
        "best_months": "Todo el año pero impredecible; localmente abundante tras plagas de roedores.",
        "did_you_know": "El único Accipitridae con disco facial definido, similar al de un búho. El disco focaliza sonidos de presas moviéndose en vegetación. Listado como Vulnerable en NSW.",
    },
    "tachyspiza_fasciata": {
        "common_name": "Azor australiano",
        "epbc_status": "No listado",
        "habitat": "Bosque denso, arbolado",
        "diagnostic": "Alas cortas y redondeadas, cola larga con bandas, iris amarillo",
        "auslan_sign": "Mano curvada, movimiento rápido en zigzag entre árboles",
        "distribution": "En toda Australia incluyendo Tasmania, además de Nueva Guinea e islas circundantes.",
        "diet": "Aves pequeñas y medianas, mamíferos pequeños (especialmente conejos), reptiles e insectos grandes.",
        "behaviour": "Cazador al acecho — se posa en dosel denso y sale en persecución rápida. Hembra notablemente más grande que el macho.",
        "migration": "Sedentario; los juveniles dispersan ampliamente tras emplumar.",
        "nesting": "Nidos de palos en árboles altos del bosque, a menudo cerca de arroyos. Pone 2–4 huevos.",
        "breeding_months": "Primavera (Sep–Nov); ~35 días de incubación; emplumado a los ~30 días.",
        "best_months": "Todo el año, pero más visible en primavera durante el cortejo cerca del nido.",
        "did_you_know": "Reclasificado de Accipiter a Tachyspiza en 2024 por filogenia molecular. Frecuentemente confundido con el Azor gris, que tiene una forma blanca pura única en Australia.",
    },
    "falco_cenchroides": {
        "common_name": "Cernícalo australiano",
        "epbc_status": "No listado",
        "habitat": "Hábitats abiertos, pastizal, agrícola",
        "diagnostic": "Cernido estacionario sobre suelo abierto, coloración rojiza, cola en abanico",
        "auslan_sign": "Mano abierta, vibración estacionaria (cernido)",
        "distribution": "En toda Australia, Tasmania, Nueva Guinea y como visitante ocasional en Nueva Zelanda.",
        "diet": "Insectos (especialmente saltamontes y escarabajos), pequeños mamíferos, reptiles y aves pequeñas.",
        "behaviour": "Cernido estacionario distintivo, cabeza fija mientras las alas compensan continuamente el viento.",
        "migration": "Parcialmente migratorio en poblaciones del sur — aves de Tasmania y Victoria se mueven al norte en otoño.",
        "nesting": "No construye nido; usa huecos de árboles, repisas de acantilados, nidos viejos de córvidos o edificios.",
        "breeding_months": "Jul–Dic; 4–5 huevos; ~28 días de incubación.",
        "best_months": "Todo el año y muy común; visible en bordes de carretera cerniéndose sobre las cunetas.",
        "did_you_know": "El único halcón australiano que se cierne sistemáticamente. A menudo regresa al mismo poste de luz año tras año. Una de las rapaces más observadas en Australia.",
    },
    "elanus_axillaris": {
        "common_name": "Milano de hombros negros",
        "epbc_status": "No listado",
        "habitat": "Pastizal, áreas agrícolas, bordes de humedales",
        "diagnostic": "Manchas negras en hombros, plumaje blanco-gris, iris rojo, cernido",
        "auslan_sign": "Ambas manos en H, cerner luego descenso corto",
        "distribution": "En toda Australia continental; más abundante en sudeste y sudoeste.",
        "diet": "Casi exclusivamente pequeños mamíferos — predominantemente el ratón doméstico introducido y roedores nativos.",
        "behaviour": "Se cierne como cernícalo pero con alas más largas; postura de 'hombros arriba' característica. Duerme en grupos comunales.",
        "migration": "Altamente nómada e irruptivo; las poblaciones se mueven grandes distancias siguiendo plagas de roedores.",
        "nesting": "Nido de palos en lo alto de árboles en campo abierto. Pone 3–4 huevos.",
        "breeding_months": "Variable, a menudo Ago–Dic pero puede criar cualquier mes con suministro sostenido de presas.",
        "best_months": "Todo el año; localmente abundante en años posteriores a buenas lluvias cuando irrumpen los roedores.",
        "did_you_know": "Tiene ojos rojos llamativos y manchas negras en los hombros. Sus números pueden multiplicarse por diez durante plagas de ratones, con milanos concentrándose en zonas afectadas desde todo el continente.",
    },
    "lophoictinia_isura": {
        "common_name": "Milano de cola cuadrada",
        "epbc_status": "Vulnerable (Ley EPBC)",
        "habitat": "Bosque maduro de eucaliptos, arbolado",
        "diagnostic": "Cola larga y cuadrada, planeo lento sobre el dosel forestal",
        "auslan_sign": "Mano plana, planeo lento con cola cuadrada demarcada",
        "distribution": "Norte y este de Australia, con poblaciones aisladas en Australia Occidental.",
        "diet": "Depredador especializado de pichones — toma polluelos, huevos, insectos grandes y reptiles.",
        "behaviour": "Planeo lento y flotante justo sobre el dosel, buscando nidos. A menudo sigue llamadas de alarma de paseriformes.",
        "migration": "Migrante parcial — la población sur (NSW/VIC) se mueve al norte a Queensland en otoño y regresa en primavera.",
        "nesting": "Nido de palos en eucaliptos altos vivos, típicamente cerca del agua. Pone 2 huevos.",
        "breeding_months": "Ago–Dic; ~40 días de incubación; emplumado a los ~65 días.",
        "best_months": "Primavera (Sep–Nov) cuando cría y está más activo sobre el dosel.",
        "did_you_know": "La única rapaz especialista de dosel en Australia. Listado como Vulnerable bajo la Ley EPBC con menos de 1.000 individuos nacionales.",
    },
    "hieraaetus_morphnoides": {
        "common_name": "Aguilucho australiano",
        "epbc_status": "No listado",
        "habitat": "Bosque abierto, bordes forestales",
        "diagnostic": "Tamaño pequeño para águila, alas anchas redondeadas, cola corta, cresta pequeña",
        "auslan_sign": "Mano compacta, movimiento pequeño y activo (tamaño pequeño + alas anchas)",
        "distribution": "En toda Australia continental en hábitat adecuado; ausente en Tasmania.",
        "diet": "Conejos, pequeños mamíferos, aves de suelo y reptiles. Captura presas más grandes de lo esperado para su tamaño.",
        "behaviour": "Planea en térmicas como una pequeña águila de cola en cuña. Dos morfos de plumaje distintos (claro y oscuro).",
        "migration": "Migrante parcial — aves del sudeste australiano se mueven al norte en invierno.",
        "nesting": "Grandes nidos de palos en árboles altos, a menudo en bordes forestales. Pone 1–2 huevos.",
        "breeding_months": "Jul–Dic (pico Ago–Oct); ~37 días de incubación; emplumado a los ~60 días.",
        "best_months": "Temporada reproductiva (Ago–Oct); aves migratorias llegan al sudeste en Jul–Ago.",
        "did_you_know": "El águila más pequeña de Australia. Ha declinado fuertemente en el sudeste australiano desde los 80 por la tala de bosques de eucaliptos.",
    },
}


# ════════════════════════════════════════════════════════════
# Other languages — only common_name is translated for now;
# remaining fields fall back to English via get_species_data().
# Native speakers are invited to extend these via PR
# (see CONTRIBUTING.md).
# ════════════════════════════════════════════════════════════
_FR = {
    "aquila_audax":           {"common_name": "Aigle d'Australie"},
    "falco_peregrinus":       {"common_name": "Faucon pèlerin"},
    "circus_assimilis":       {"common_name": "Busard tacheté"},
    "tachyspiza_fasciata":    {"common_name": "Autour à collier roux"},
    "falco_cenchroides":      {"common_name": "Crécerelle d'Australie"},
    "elanus_axillaris":       {"common_name": "Élanion d'Australie"},
    "lophoictinia_isura":     {"common_name": "Milan à queue carrée"},
    "hieraaetus_morphnoides": {"common_name": "Aigle nain"},
}

_PT = {
    "aquila_audax":           {"common_name": "Águia-de-rabadilha-branca"},
    "falco_peregrinus":       {"common_name": "Falcão-peregrino"},
    "circus_assimilis":       {"common_name": "Tartaranhão-malhado"},
    "tachyspiza_fasciata":    {"common_name": "Açor-australiano"},
    "falco_cenchroides":      {"common_name": "Peneireiro-australiano"},
    "elanus_axillaris":       {"common_name": "Peneireiro-de-ombros-pretos"},
    "lophoictinia_isura":     {"common_name": "Milhafre-de-cauda-quadrada"},
    "hieraaetus_morphnoides": {"common_name": "Águia-pequena-australiana"},
}

_IT = {
    "aquila_audax":           {"common_name": "Aquila australiana"},
    "falco_peregrinus":       {"common_name": "Falco pellegrino"},
    "circus_assimilis":       {"common_name": "Albanella maculata"},
    "tachyspiza_fasciata":    {"common_name": "Astore bruno"},
    "falco_cenchroides":      {"common_name": "Gheppio australiano"},
    "elanus_axillaris":       {"common_name": "Nibbio bianco australiano"},
    "lophoictinia_isura":     {"common_name": "Nibbio dalla coda quadra"},
    "hieraaetus_morphnoides": {"common_name": "Aquila minore"},
}

_DE = {
    "aquila_audax":           {"common_name": "Keilschwanzadler"},
    "falco_peregrinus":       {"common_name": "Wanderfalke"},
    "circus_assimilis":       {"common_name": "Fleckenweihe"},
    "tachyspiza_fasciata":    {"common_name": "Habichtsweihe"},
    "falco_cenchroides":      {"common_name": "Graubart-Falke"},
    "elanus_axillaris":       {"common_name": "Schwarzschulteraar"},
    "lophoictinia_isura":     {"common_name": "Schwalbenmilan"},
    "hieraaetus_morphnoides": {"common_name": "Zwergadler"},
}

_ZH = {
    "aquila_audax":           {"common_name": "楔尾雕"},
    "falco_peregrinus":       {"common_name": "游隼"},
    "circus_assimilis":       {"common_name": "斑泽鵟"},
    "tachyspiza_fasciata":    {"common_name": "棕鹰"},
    "falco_cenchroides":      {"common_name": "南清隼"},
    "elanus_axillaris":       {"common_name": "黑肩鸢"},
    "lophoictinia_isura":     {"common_name": "方尾鸢"},
    "hieraaetus_morphnoides": {"common_name": "小雕"},
}

_JA = {
    "aquila_audax":           {"common_name": "オナガイヌワシ"},
    "falco_peregrinus":       {"common_name": "ハヤブサ"},
    "circus_assimilis":       {"common_name": "ホシハイイロチュウヒ"},
    "tachyspiza_fasciata":    {"common_name": "ヒメコノハオオタカ"},
    "falco_cenchroides":      {"common_name": "オーストラリアチョウゲンボウ"},
    "elanus_axillaris":       {"common_name": "クロカタシロガシラトビ"},
    "lophoictinia_isura":     {"common_name": "カクオトビ"},
    "hieraaetus_morphnoides": {"common_name": "ヒメイヌワシ"},
}

_KO = {
    "aquila_audax":           {"common_name": "쐐기꼬리수리"},
    "falco_peregrinus":       {"common_name": "매"},
    "circus_assimilis":       {"common_name": "얼룩개구리매"},
    "tachyspiza_fasciata":    {"common_name": "갈색새매"},
    "falco_cenchroides":      {"common_name": "호주황조롱이"},
    "elanus_axillaris":       {"common_name": "검은어깨솔개"},
    "lophoictinia_isura":     {"common_name": "각진꼬리솔개"},
    "hieraaetus_morphnoides": {"common_name": "꼬마독수리"},
}

_RU = {
    "aquila_audax":           {"common_name": "Клинохвостый орёл"},
    "falco_peregrinus":       {"common_name": "Сапсан"},
    "circus_assimilis":       {"common_name": "Пятнистый лунь"},
    "tachyspiza_fasciata":    {"common_name": "Бурый ястреб"},
    "falco_cenchroides":      {"common_name": "Серая пустельга"},
    "elanus_axillaris":       {"common_name": "Чёрнокрылый дымчатый коршун"},
    "lophoictinia_isura":     {"common_name": "Квадратнохвостый коршун"},
    "hieraaetus_morphnoides": {"common_name": "Малый орёл"},
}


# ════════════════════════════════════════════════════════════
# Public API
# ════════════════════════════════════════════════════════════
SPECIES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "en": _EN,
    "es": _ES,
    "fr": _FR,
    "pt": _PT,
    "it": _IT,
    "de": _DE,
    "zh": _ZH,
    "ja": _JA,
    "ko": _KO,
    "ru": _RU,
}


def get_species_data(lang: str = "en") -> dict[str, dict[str, str]]:
    """
    Return per-species data for the requested language with English
    fallback applied field by field. Languages other than 'es' and 'en'
    currently translate only the common name; other fields fall back
    to English. Native speakers are encouraged to extend.
    """
    overrides = SPECIES_I18N.get(lang, {})
    out: dict[str, dict[str, str]] = {}
    for species_key, en_block in _EN.items():
        merged = dict(en_block)                # start with English
        for field, value in overrides.get(species_key, {}).items():
            if value:                           # non-empty overrides
                merged[field] = value
        out[species_key] = merged
    return out
