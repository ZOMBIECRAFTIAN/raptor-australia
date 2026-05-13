"""
ALA Behavior Video Downloader
=========================================================
Pulls video media (≤ 1 per species) from the Atlas of Living
Australia and saves them to ``gui/static/behavior_videos/``
under the canonical filename ``<species_key>.mp4``.

iNaturalist does not host videos — only photos and audio — so
ALA is the right open-licence source for behaviour footage.

Properties:
- No API key (ALA is fully open).
- Resumable: skips species that already have a behavior video on disk.
- Rate-limited (1 req/s) and respects ALA's documented retries.
- Probes the same fallback strategies as the image downloader
  (lsid → species: → genus+epithet) so synonym-affected species
  (Tachyspiza/Accipiter) still work.
- Writes a sidecar ``attribution.csv`` with source URLs and licences.

Usage (from project root):
    python notebooks/download_ala_videos.py --dry-run
    python notebooks/download_ala_videos.py
    python notebooks/download_ala_videos.py --species aquila_audax
    python notebooks/download_ala_videos.py --max-mb 8

Notes
- ALA serves video media at ``images.ala.org.au/image/<id>/original``
  (the endpoint name is misleading — it serves any media type).
- Many ALA records have video URLs hosted on YouTube, Vimeo, etc.
  This script downloads ONLY direct media links (.mp4, .webm, .mov)
  to keep the licence chain auditable; YouTube embeds are skipped.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR     = Path(__file__).resolve().parent.parent
OUTPUT_DIR   = BASE_DIR / "gui" / "static" / "behavior_videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ATTRIBUTION  = OUTPUT_DIR / "attribution.csv"

ALA_BASE     = "https://biocache-ws.ala.org.au/ws/occurrences/search"
ALA_NAME_SVC = "https://bie-ws.ala.org.au/ws/search.json"
ALA_MEDIA    = "https://images.ala.org.au/image/{image_id}/original"
USER_AGENT   = "RaptorAU-MPhilProject/1.2 (research; Brian Fernandez)"
TIMEOUT_SEC  = 60
SLEEP_BETWEEN_REQUESTS = 1.0
PAGE_SIZE    = 30
DEFAULT_MAX_MB = 12

# Same multi-name map as the image downloader (handles 2024
# Accipiter→Tachyspiza reclassification).
SPECIES_MAP: dict[str, list[str]] = {
    "aquila_audax":           ["Aquila audax"],
    "falco_peregrinus":       ["Falco peregrinus"],
    "circus_assimilis":       ["Circus assimilis"],
    "tachyspiza_fasciata":    ["Tachyspiza fasciata", "Accipiter fasciatus"],
    "falco_cenchroides":      ["Falco cenchroides"],
    "elanus_axillaris":       ["Elanus axillaris"],
    "lophoictinia_isura":     ["Lophoictinia isura"],
    "hieraaetus_morphnoides": ["Hieraaetus morphnoides"],
}


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as r:
        return json.loads(r.read().decode("utf-8"))


def http_head(url: str) -> tuple[int, str]:
    """Returns (status, content_type)."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as r:
            return r.status, r.headers.get("Content-Type", "")
    except Exception as e:
        return 0, str(e)


def http_download(url: str, dest: Path, max_bytes: int) -> bool:
    """Stream up to max_bytes; returns True on success."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as r:
            chunk_size = 64 * 1024
            written = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = r.read(chunk_size)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > max_bytes:
                        f.close()
                        dest.unlink(missing_ok=True)
                        return False
                    f.write(chunk)
        return written > 0
    except Exception as e:
        print(f"  download error: {e}")
        if dest.exists():
            dest.unlink(missing_ok=True)
        return False


def resolve_lsid(name: str) -> str | None:
    params = {"q": name, "pageSize": "10"}
    url = f"{ALA_NAME_SVC}?{urllib.parse.urlencode(params)}"
    try:
        data = http_get_json(url)
    except Exception:
        return None
    results = (data.get("searchResults") or {}).get("results") or []
    species_hits = [r for r in results
                    if (r.get("rank") or "").lower() == "species"
                    and (r.get("guid") or "").startswith("http")
                    and (r.get("name") or "").lower() == name.lower()]
    if species_hits:
        return species_hits[0]["guid"]
    taxa = [r for r in results
            if (r.get("guid") or "").startswith("http")]
    return taxa[0]["guid"] if taxa else None


def search_video_records(name: str, lsid: str | None,
                         page: int = 0) -> dict:
    """Try lsid first, fall back to species:, then a fielded fallback."""
    queries: list[str] = []
    if lsid:
        queries.append(f'lsid:"{lsid}"')
    queries.append(f'species:"{name}"')
    parts = name.split()
    if len(parts) >= 2:
        queries.append(
            f'genus:"{parts[0]}" AND specificEpithet:"{parts[1]}"')

    last_data = {"totalRecords": 0, "occurrences": []}
    for q in queries:
        params = {
            "q":        q,
            "fq":       "multimedia:Video",
            "pageSize": str(PAGE_SIZE),
            "start":    str(page * PAGE_SIZE),
            "facet":    "off",
            "fl":       "id,scientificName,multimedia,images,imageUrls,"
                        "rights,license",
        }
        url = f"{ALA_BASE}?{urllib.parse.urlencode(params)}"
        try:
            data = http_get_json(url)
        except Exception as e:
            print(f"  search error ({q[:30]}): {e}")
            continue
        if (data.get("totalRecords") or 0) > 0:
            return data
        last_data = data
        time.sleep(SLEEP_BETWEEN_REQUESTS / 2)
    return last_data


def extract_media_ids(occ: dict) -> list[str]:
    ids: list[str] = []
    for m in occ.get("multimedia") or []:
        if isinstance(m, dict) and m.get("imageId"):
            ids.append(m["imageId"])
    for u in occ.get("imageUrls") or []:
        try:
            parts = u.split("/image/")
            if len(parts) > 1:
                ids.append(parts[1].split("/")[0])
        except Exception:
            pass
    seen, out = set(), []
    for x in ids:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def is_video(content_type: str) -> bool:
    if not content_type:
        return False
    return content_type.startswith("video/")


def append_attribution(species_key: str, image_id: str,
                       occurrence_id: str, license_str: str) -> None:
    fresh = not ATTRIBUTION.exists()
    with open(ATTRIBUTION, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if fresh:
            w.writerow(["species_key", "filename", "ala_image_id",
                        "occurrence_id", "license", "downloaded_on"])
        w.writerow([
            species_key, f"{species_key}.mp4", image_id,
            occurrence_id, license_str or "unknown",
            time.strftime("%Y-%m-%d"),
        ])


def download_for_species(species_key: str,
                         names: list[str],
                         max_bytes: int,
                         dry_run: bool) -> bool:
    print(f"\n=== {species_key}  ({' / '.join(names)}) ===")

    # Skip if already present
    for ext in ("mp4", "webm", "mov"):
        existing = OUTPUT_DIR / f"{species_key}.{ext}"
        if existing.exists():
            print(f"  → already on disk ({existing.name}); skipping.")
            return True

    for name in names:
        lsid = resolve_lsid(name)
        if lsid:
            print(f"  '{name}' LSID: {lsid}")
        else:
            print(f"  '{name}' LSID: not found")

        page = 0
        while page < 5:                       # cap at 5 pages per name
            data = search_video_records(name, lsid, page)
            total = data.get("totalRecords") or 0
            occs = data.get("occurrences") or []
            if page == 0:
                print(f"  ALA reports {total} video records under '{name}'")
            if not occs:
                break

            for occ in occs:
                license_str = (occ.get("license") or
                               occ.get("rights") or "")
                occ_id = occ.get("id") or ""
                for media_id in extract_media_ids(occ):
                    url = ALA_MEDIA.format(image_id=media_id)
                    status, ctype = http_head(url)
                    if not is_video(ctype):
                        time.sleep(SLEEP_BETWEEN_REQUESTS / 2)
                        continue
                    print(f"  candidate {media_id[:8]}…  ({ctype})  "
                          f"license={license_str or 'unknown'}")
                    if dry_run:
                        return True
                    dst = OUTPUT_DIR / f"{species_key}.mp4"
                    ok = http_download(url, dst, max_bytes)
                    if ok and dst.exists() and dst.stat().st_size > 100_000:
                        print(f"  ✓ wrote {dst.name} "
                              f"({dst.stat().st_size/1e6:.1f} MB)")
                        append_attribution(species_key, media_id,
                                           str(occ_id), license_str)
                        return True
                    elif dst.exists():
                        print(f"  ⊘ exceeded max_mb; trying next candidate")
                    time.sleep(SLEEP_BETWEEN_REQUESTS)

            page += 1
            time.sleep(SLEEP_BETWEEN_REQUESTS)

    print(f"  ✗ no usable video found for {species_key}")
    return False


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--species", default=None,
                   help="Limit to one species_key")
    p.add_argument("--max-mb", type=float, default=DEFAULT_MAX_MB,
                   help=f"Max video size in MB (default {DEFAULT_MAX_MB})")
    p.add_argument("--dry-run", action="store_true",
                   help="Just probe; don't write any files")
    return p.parse_args()


def main():
    args = parse_args()
    keys = [args.species] if args.species else list(SPECIES_MAP.keys())
    if args.species and args.species not in SPECIES_MAP:
        raise SystemExit(f"Unknown species: {args.species}")

    print(f"ALA video downloader — max_mb={args.max_mb} · dry_run={args.dry_run}")
    print(f"OUTPUT_DIR = {OUTPUT_DIR}")
    max_bytes = int(args.max_mb * 1_000_000)

    found, missing = [], []
    for key in keys:
        ok = download_for_species(key, SPECIES_MAP[key],
                                  max_bytes, args.dry_run)
        (found if ok else missing).append(key)

    print(f"\n=== SUMMARY ===")
    print(f"  videos available:   {len(found)}/{len(keys)}")
    if missing:
        print(f"  missing/unfound:    {missing}")
        print(f"\n  For species without ALA videos, the README at")
        print(f"  gui/static/behavior_videos/README.md lists alternative")
        print(f"  CC-licensed sources (Wikimedia Commons, YouTube CC, etc.).")


if __name__ == "__main__":
    main()
