"""
Atlas of Living Australia (ALA) — Image Downloader
=========================================================
Pulls additional raptor occurrence images from ALA to expand
the dataset already curated from iNaturalist Australia.

Saves files into:
    dataset/raw/<species_key>/ala_<imageId>.jpg

Properties:
- Sin API key (ALA es totalmente abierta).
- Resumable: si ala_<id>.jpg ya existe, lo salta.
- Rate-limited: 1 request/segundo por defecto (uso académico).
- Dedup contra archivos existentes por imageId.
- Soporta --dry-run para ver qué bajaría sin escribir.
- Soporta --species para limitar a una especie.

Uso típico (Windows / Linux / macOS):
    python download_ala_images.py
    python download_ala_images.py --target 200
    python download_ala_images.py --species aquila_audax
    python download_ala_images.py --dry-run

Documentación API:
    https://api.ala.org.au/
    https://biocache-ws.ala.org.au/ws/
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

# ─── Configuración ──────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
DATASET_DIR  = BASE_DIR / "dataset" / "raw"

ALA_BASE     = "https://biocache-ws.ala.org.au/ws/occurrences/search"
ALA_NAME_SVC = "https://bie-ws.ala.org.au/ws/search.json"
ALA_IMG_FMT  = "https://images.ala.org.au/image/{image_id}/large"
USER_AGENT   = "RaptorAU-MPhilProject/0.1 (research; Brian Fernandez)"
TIMEOUT_SEC  = 30
SLEEP_BETWEEN_REQUESTS = 1.0     # politeness towards the ALA API
PAGE_SIZE    = 100               # records per occurrence search page

# Map from project_key → list of accepted scientific names to query.
# Multiple names allow handling taxonomic synonyms — e.g. ALA still
# stores most Brown Goshawk records under the older "Accipiter fasciatus"
# even though the species was moved to genus Tachyspiza in 2024.
SPECIES_MAP: dict[str, list[str]] = {
    "aquila_audax":           ["Aquila audax"],
    "falco_peregrinus":       ["Falco peregrinus"],
    "circus_assimilis":       ["Circus assimilis"],
    "tachyspiza_fasciata":    ["Tachyspiza fasciata",
                               "Accipiter fasciatus"],   # 2024 reclassification
    "falco_cenchroides":      ["Falco cenchroides"],
    "elanus_axillaris":       ["Elanus axillaris"],
    "lophoictinia_isura":     ["Lophoictinia isura"],
    "hieraaetus_morphnoides": ["Hieraaetus morphnoides"],
}

# Some images come back without a usable id; tolerate that gracefully.
DEFAULT_TARGET_PER_SPECIES = 300


# ─── Funciones auxiliares ───────────────────────────────
def http_get_json(url: str) -> dict:
    """GET JSON from ALA with a custom UA and timeout."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get_bytes(url: str) -> bytes:
    """GET raw bytes (used for downloading images)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        return resp.read()


def resolve_lsid(scientific_name: str) -> str | None:
    """
    Use the ALA names service (BIE) to resolve a scientific name
    to its taxonomic LSID/guid. Filters out non-taxon hits
    (data resource IDs, etc.). Returns None if no taxonomic match.
    """
    params = {"q": scientific_name, "pageSize": "10"}
    url    = f"{ALA_NAME_SVC}?{urllib.parse.urlencode(params)}"
    try:
        data = http_get_json(url)
    except Exception as e:
        print(f"  [name service] error: {e}")
        return None
    results = (data.get("searchResults") or {}).get("results") or []
    if not results:
        return None

    # A real taxon hit has a rank and a guid that's a URL
    # (https://biodiversity.org.au/... or https://id.biodiversity.org.au/...).
    # Reject hits like "ALA_DR30474_877" (those are data resources).
    def looks_like_taxon_lsid(g: str | None) -> bool:
        return bool(g) and g.startswith("http")

    species_hits = [r for r in results
                    if (r.get("rank") or "").lower() == "species"
                    and looks_like_taxon_lsid(r.get("guid"))
                    and (r.get("name") or "").lower() ==
                        scientific_name.lower()]
    if species_hits:
        return species_hits[0].get("guid")

    # Fall back to any taxonomic LSID
    taxon_hits = [r for r in results
                  if looks_like_taxon_lsid(r.get("guid"))
                  and (r.get("rank") or "").lower() in
                      ("species", "subspecies", "genus")]
    if taxon_hits:
        return taxon_hits[0].get("guid")
    return None


def build_query_strategies(scientific_name: str,
                            lsid: str | None) -> list[tuple[str, str]]:
    """
    Yield (strategy_label, q_param) pairs to try in order. The first
    strategy that returns occurrences > 0 is the one we use.
    """
    queries: list[tuple[str, str]] = []
    if lsid and lsid.startswith("http"):
        queries.append(("lsid", f'lsid:"{lsid}"'))
    # Species accepted name field
    queries.append(("species_field", f'species:"{scientific_name}"'))
    # Genus + specificEpithet
    parts = scientific_name.split()
    if len(parts) >= 2:
        genus, species = parts[0], parts[1]
        queries.append((
            "genus+epithet",
            f'genus:"{genus}" AND specificEpithet:"{species}"'
        ))
    # Phrase across all fields (lowest precision, highest recall)
    queries.append(("phrase", f'"{scientific_name}"'))
    return queries


def search_occurrences(q_param: str,
                       page: int,
                       page_size: int = PAGE_SIZE) -> dict:
    """
    Query ALA biocache occurrences with images using a custom q_param.
    """
    params = {
        "q":        q_param,
        "fq":       "multimedia:Image",
        "pageSize": str(page_size),
        "start":    str(page * page_size),
        "facet":    "off",
        "fl":       "id,scientificName,imageUrls,images,multimedia",
    }
    url = f"{ALA_BASE}?{urllib.parse.urlencode(params)}"
    return http_get_json(url)


def pick_working_strategy(scientific_name: str,
                          lsid: str | None) -> tuple[str, str] | None:
    """
    Probe each strategy with a tiny request and return the first one
    that reports >0 occurrences. Probes use pageSize=1 so they're cheap.
    """
    for label, q in build_query_strategies(scientific_name, lsid):
        try:
            url = (f"{ALA_BASE}?"
                   f"{urllib.parse.urlencode({'q': q, 'fq': 'multimedia:Image', 'pageSize': '1', 'facet': 'off'})}")
            data = http_get_json(url)
            n = data.get("totalRecords") or 0
            print(f"  probe '{label}': {n} records")
            if n > 0:
                return (label, q)
        except Exception as e:
            print(f"  probe '{label}' error: {e}")
        time.sleep(SLEEP_BETWEEN_REQUESTS / 2)
    return None


def extract_image_ids(occurrence: dict) -> list[str]:
    """
    ALA can put image identifiers in several fields depending on the
    record source. We try them in priority order.
    """
    ids: list[str] = []

    # Most occurrences expose 'imageUrls' = list of full URLs.
    for u in occurrence.get("imageUrls") or []:
        # URL pattern: .../image/<imageId>/large or /original
        # We extract the imageId path segment.
        try:
            parts = u.split("/image/")
            if len(parts) > 1:
                image_id = parts[1].split("/")[0]
                if image_id:
                    ids.append(image_id)
        except Exception:
            pass

    # 'images' may also be present (list of image ids directly).
    for i in occurrence.get("images") or []:
        if isinstance(i, str) and i:
            ids.append(i)
        elif isinstance(i, dict) and i.get("imageId"):
            ids.append(i["imageId"])

    # 'multimedia' sometimes has more ids.
    for m in occurrence.get("multimedia") or []:
        if isinstance(m, dict) and m.get("imageId"):
            ids.append(m["imageId"])

    # Dedup keeping order.
    seen, out = set(), []
    for x in ids:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def existing_image_ids(species_dir: Path) -> set[str]:
    """Return the set of ALA imageIds already on disk."""
    if not species_dir.exists():
        return set()
    return {
        f.stem.replace("ala_", "")
        for f in species_dir.glob("ala_*.jpg")
    }


# ─── Descarga principal ─────────────────────────────────
def download_for_species(species_key: str,
                         scientific_names: list[str],
                         target: int,
                         dry_run: bool) -> dict:
    species_dir = DATASET_DIR / species_key
    species_dir.mkdir(parents=True, exist_ok=True)

    already   = existing_image_ids(species_dir)
    saved     = 0
    seen_ids: set[str] = set(already)
    pages_consumed = 0

    print(f"\n=== {species_key}  ({' / '.join(scientific_names)}) ===")
    print(f"  pre-existing ALA images on disk: {len(already)}")

    # Build a list of (name, q_param) pairs — one per accepted name.
    name_strategies: list[tuple[str, str]] = []
    for sci in scientific_names:
        if saved >= target:
            break
        lsid = resolve_lsid(sci)
        if lsid:
            print(f"  '{sci}' LSID: {lsid}")
        else:
            print(f"  '{sci}' LSID: not found "
                  f"(will fall back to species/genus search)")
        chosen = pick_working_strategy(sci, lsid)
        if chosen is None:
            print(f"  '{sci}' no strategy returned records — skipping")
            continue
        label, q_param = chosen
        print(f"  '{sci}' strategy: {label}  | q = {q_param}")
        name_strategies.append((sci, q_param))

    if not name_strategies:
        print(f"  no working strategy across {len(scientific_names)} "
              f"name(s) — skipping {species_key}")
        return {"species": species_key, "saved": 0}

    # Iterate through each accepted name's q_param until target is reached.
    for sci, q_param in name_strategies:
        if saved >= target:
            break
        print(f"  -- pulling under '{sci}' --")
        page = 0
        pages_for_this_name = 0
        while saved < target:
            try:
                data = search_occurrences(q_param, page=page)
            except Exception as e:
                print(f"  [page {page}] search error: {e}")
                break

            occs  = data.get("occurrences") or []
            total = data.get("totalRecords")
            if page == 0:
                print(f"  ALA reports {total} occurrences with images")

            if not occs:
                print(f"  [page {page}] no more results.")
                break

            for occ in occs:
                for image_id in extract_image_ids(occ):
                    if image_id in seen_ids:
                        continue
                    seen_ids.add(image_id)

                    out_path = species_dir / f"ala_{image_id}.jpg"
                    if dry_run:
                        saved += 1
                        if saved >= target:
                            break
                        continue

                    try:
                        url  = ALA_IMG_FMT.format(image_id=image_id)
                        blob = http_get_bytes(url)
                        if len(blob) < 5_000:
                            # almost certainly an HTML "not found" page
                            continue
                        out_path.write_bytes(blob)
                        saved += 1
                        if saved % 25 == 0:
                            print(f"  saved {saved}/{target}")
                    except Exception as e:
                        print(f"  image {image_id} failed: {e}")
                    finally:
                        time.sleep(SLEEP_BETWEEN_REQUESTS)

                    if saved >= target:
                        break
                if saved >= target:
                    break

            pages_consumed     += 1
            pages_for_this_name += 1
            page               += 1
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            # Safety break per-name: avoid burning more than 50 pages
            # on a single accepted name without reaching the target.
            if pages_for_this_name >= 50:
                print(f"  [safety] aborting '{sci}' after 50 pages")
                break

    print(f"  -> downloaded {saved} new images ({'DRY RUN' if dry_run else 'WROTE'})")
    return {"species": species_key, "saved": saved}


# ─── CLI ────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--species", default=None,
                   help="Limit to one species_key (default: all 8)")
    p.add_argument("--target", type=int, default=DEFAULT_TARGET_PER_SPECIES,
                   help=f"Images per species target (default: {DEFAULT_TARGET_PER_SPECIES})")
    p.add_argument("--dry-run", action="store_true",
                   help="Don't write files, just report counts")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.species:
        if args.species not in SPECIES_MAP:
            raise SystemExit(f"Unknown species: {args.species}. "
                             f"Valid: {list(SPECIES_MAP)}")
        species_iter: Iterable[tuple[str, list[str]]] = [
            (args.species, SPECIES_MAP[args.species])
        ]
    else:
        species_iter = SPECIES_MAP.items()

    print(f"ALA downloader — target: {args.target} images/species — "
          f"dry_run: {args.dry_run}")
    print(f"DATASET_DIR = {DATASET_DIR}")

    summary = []
    for key, sci_names in species_iter:
        # Backwards compat: if SPECIES_MAP entry is a string, wrap it.
        if isinstance(sci_names, str):
            sci_names = [sci_names]
        summary.append(
            download_for_species(key, sci_names, args.target, args.dry_run)
        )

    print("\n=== SUMMARY ===")
    for r in summary:
        print(f"  {r['species']:<25}  +{r['saved']}")
    total = sum(r["saved"] for r in summary)
    print(f"  TOTAL new: {total}")


if __name__ == "__main__":
    main()
