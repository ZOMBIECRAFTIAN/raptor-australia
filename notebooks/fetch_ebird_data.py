"""
eBird Enrichment Fetcher
=========================================================
Pulls recent-observation data from the eBird API for the 8
raptor species in the project and saves a single aggregated
``results/ebird_enrichment.json`` that the species guide can
consume to display Merlin-style "recently seen" information.

eBird does NOT expose images (those live in Cornell's
Macaulay Library under a separate gated API). What we use
eBird for is *observation metadata*:

    - How many sightings in the last 30 days
    - Where the species was last reported
    - The most active hotspots for the species in Australia
    - Per-state distribution of sightings

Combined with the project's own CNN identifications, this
turns the species guide into a "what the model recognises +
where it's actually being seen right now" hybrid — original
content for the MPhil proposal.

SECURITY
- Reads ``EBIRD_API_KEY`` from a local ``.env`` file or the
  environment. The key is NEVER hard-coded in source.
- ``.env`` is gitignored, so the secret never reaches GitHub.

Usage (from project root, with ``raptor_env`` active):
    # 1. Create .env at the repo root with one line:
    #        EBIRD_API_KEY=your_actual_key_here
    # 2. Run:
    python notebooks/fetch_ebird_data.py
    python notebooks/fetch_ebird_data.py --species aquila_audax
    python notebooks/fetch_ebird_data.py --back 60   # last 60 days
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
ENV_PATH    = BASE_DIR / ".env"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH    = RESULTS_DIR / "ebird_enrichment.json"

# eBird API
EBIRD_BASE = "https://api.ebird.org/v2"
USER_AGENT = "RaptorAU-MPhilProject/1.2 (research)"
TIMEOUT    = 30
SLEEP      = 0.6                       # ~1.5 req/s — polite

# Scientific names → eBird taxonomy lookup target
# (eBird species codes are resolved at runtime via /ref/taxonomy)
SPECIES_SCI = {
    "aquila_audax":           "Aquila audax",
    "falco_peregrinus":       "Falco peregrinus",
    "circus_assimilis":       "Circus assimilis",
    "tachyspiza_fasciata":    "Accipiter fasciatus",   # eBird still uses old genus
    "falco_cenchroides":      "Falco cenchroides",
    "elanus_axillaris":       "Elanus axillaris",
    "lophoictinia_isura":     "Lophoictinia isura",
    "hieraaetus_morphnoides": "Hieraaetus morphnoides",
}


# ─── Secret loading ─────────────────────────────────────
def load_dotenv() -> None:
    """Populate ``os.environ`` from .env (KEY=VALUE per line)."""
    if not ENV_PATH.exists():
        return
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_ebird_key() -> str:
    load_dotenv()
    key = os.getenv("EBIRD_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "ERROR: EBIRD_API_KEY not set.\n"
            "  Create a file `.env` at the project root with this single line:\n"
            "      EBIRD_API_KEY=<your_key_from_ebird.org/api/keygen>\n"
            "  `.env` is gitignored — the key stays on your machine."
        )
    if len(key) < 8 or " " in key:
        raise SystemExit("ERROR: EBIRD_API_KEY looks malformed.")
    return key


# ─── HTTP helpers ───────────────────────────────────────
def ebird_get(path: str, params: dict, key: str):
    """GET an eBird API endpoint; returns parsed JSON or raises."""
    url = f"{EBIRD_BASE}{path}"
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "X-eBirdApiToken": key},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


# ─── Taxonomy resolution ────────────────────────────────
_taxon_cache: dict[str, str] = {}


def resolve_species_code(sci_name: str, key: str) -> str | None:
    """Return the eBird 6-character species code for a scientific name."""
    if sci_name in _taxon_cache:
        return _taxon_cache[sci_name]
    try:
        data = ebird_get("/ref/taxonomy/ebird",
                         {"fmt": "json", "species": sci_name}, key)
    except Exception as e:
        print(f"  taxonomy lookup failed for '{sci_name}': {e}")
        return None
    if not data:
        return None
    code = data[0].get("speciesCode")
    _taxon_cache[sci_name] = code
    return code


# ─── Per-species enrichment ─────────────────────────────
def fetch_recent_observations(species_code: str, back_days: int,
                              key: str) -> list:
    """All recent AU observations for one species."""
    try:
        return ebird_get(
            f"/data/obs/AU/recent/{species_code}",
            {"back": back_days, "maxResults": "500"}, key)
    except Exception as e:
        print(f"  observations error: {e}")
        return []


def summarise(observations: list) -> dict:
    """Reduce eBird's per-record list to a compact summary."""
    if not observations:
        return {
            "recent_count": 0,
            "last_seen": None,
            "top_locations": [],
            "top_states": [],
            "last_observer": None,
        }

    # Each observation has obsDt, locName, subnational1Code, ...
    locations: Counter = Counter()
    states:    Counter = Counter()
    for o in observations:
        loc = o.get("locName") or "unknown"
        locations[loc] += int(o.get("howMany") or 1)
        # subnational1Code looks like "AU-NSW"
        sn = o.get("subnational1Code") or ""
        states[sn] += int(o.get("howMany") or 1)

    # Most recent
    obs_sorted = sorted(observations,
                        key=lambda o: o.get("obsDt") or "",
                        reverse=True)
    latest = obs_sorted[0]

    return {
        "recent_count":   len(observations),
        "last_seen":      {
            "date":     latest.get("obsDt"),
            "location": latest.get("locName"),
            "state":    latest.get("subnational1Code"),
            "lat":      latest.get("lat"),
            "lng":      latest.get("lng"),
            "count":    latest.get("howMany"),
        },
        "top_locations": [
            {"location": loc, "count": n}
            for loc, n in locations.most_common(5)
        ],
        "top_states": [
            {"state": st, "count": n}
            for st, n in states.most_common(8)
        ],
    }


# ─── Main pipeline ──────────────────────────────────────
def run(species_filter: str | None, back_days: int):
    key = get_ebird_key()
    print(f"eBird enrichment fetcher — back {back_days} days · "
          f"region: AU\n")

    out: dict = {
        "_meta": {
            "region":     "AU",
            "back_days":  back_days,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source":     "eBird API v2 — observations endpoint",
            "note":       "Recent observation metadata only. eBird does "
                          "not provide images via the public API; those "
                          "live in Macaulay Library under separate terms.",
        },
        "species": {},
    }

    targets = ({species_filter: SPECIES_SCI[species_filter]}
               if species_filter else SPECIES_SCI)

    for sp_key, sci_name in targets.items():
        print(f"  [{sp_key:<28}] resolving {sci_name} …")
        code = resolve_species_code(sci_name, key)
        if not code:
            print(f"      ✗ no eBird species code found")
            out["species"][sp_key] = {
                "scientific_name": sci_name,
                "species_code":    None,
                "error":           "species code lookup failed",
            }
            continue
        print(f"      eBird code: {code}")
        time.sleep(SLEEP)

        obs = fetch_recent_observations(code, back_days, key)
        summary = summarise(obs)
        summary["scientific_name"] = sci_name
        summary["species_code"]    = code
        out["species"][sp_key] = summary
        print(f"      {summary['recent_count']:>3} recent observations · "
              f"last seen "
              f"{summary['last_seen']['date'] if summary['last_seen'] else '—'}")
        time.sleep(SLEEP)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Wrote {OUT_PATH}")
    print(f"  ({sum(s.get('recent_count', 0) for s in out['species'].values())} "
          f"total observations across {len(out['species'])} species)")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--species", default=None,
                   help="Limit to one species_key")
    p.add_argument("--back", type=int, default=30,
                   help="How many days back to query (1–30, eBird's max)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.species, args.back)
