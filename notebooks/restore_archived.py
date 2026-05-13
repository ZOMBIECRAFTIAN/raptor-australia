"""
Restore images from dataset/raw_archive/ back into dataset/raw/.

Pairs with ``filter_ala_quality.py`` — useful when the previous
filter run was too aggressive and you want some of those images
back. Reads ``dataset/metadata/quality_filter.csv`` to know why
each image was archived, and lets you restore selectively by
reason.

Usage (from project root):
    # Restore EVERYTHING (back to pre-filter state)
    python notebooks/restore_archived.py --all

    # Restore only the images rejected purely for being small —
    # these had a real bird in them; we just want to keep them
    # for training even if low-resolution.
    python notebooks/restore_archived.py --reasons too_small,too_small_bird

    # Limit to one species
    python notebooks/restore_archived.py --reasons too_small \\
        --species aquila_audax

    # Dry run (no files moved)
    python notebooks/restore_archived.py --all --dry-run
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

BASE_DIR     = Path(__file__).resolve().parent.parent
DATASET_DIR  = BASE_DIR / "dataset" / "raw"
ARCHIVE_DIR  = BASE_DIR / "dataset" / "raw_archive"
METADATA_DIR = BASE_DIR / "dataset" / "metadata"
LOG_PATH     = METADATA_DIR / "quality_filter.csv"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--all", action="store_true",
                   help="Restore every archived image regardless of reason.")
    p.add_argument("--reasons", default="",
                   help="Comma-separated list of reason prefixes to restore "
                        "(e.g. 'too_small,too_small_bird').")
    p.add_argument("--species", default=None,
                   help="Limit to one species_key.")
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would be moved; don't move anything.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not args.all and not args.reasons:
        raise SystemExit("Specify either --all or --reasons <list>.")

    selected_reasons = {r.strip()
                        for r in args.reasons.split(",") if r.strip()}

    moved = 0
    skipped_missing = 0
    by_reason: dict[str, int] = {}

    if args.all:
        # Walk the archive directly — works even if the audit log is missing
        species_dirs = sorted(p for p in ARCHIVE_DIR.iterdir() if p.is_dir())
        if args.species:
            species_dirs = [p for p in species_dirs if p.name == args.species]
        for sp_dir in species_dirs:
            sp = sp_dir.name
            dst = DATASET_DIR / sp
            dst.mkdir(parents=True, exist_ok=True)
            files = list(sp_dir.iterdir())
            print(f"  [{sp:<28}] restoring {len(files)} files…")
            for f in files:
                if not args.dry_run:
                    shutil.move(str(f), str(dst / f.name))
                moved += 1
            # Try to remove the now-empty species archive folder
            if not args.dry_run:
                try:
                    sp_dir.rmdir()
                except OSError:
                    pass
    else:
        # Reason-driven restore using the audit log
        if not LOG_PATH.exists():
            raise SystemExit(
                f"No audit log at {LOG_PATH}. Use --all instead.")
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for r in rows:
            sp = r["species_key"]
            if args.species and sp != args.species:
                continue
            if int(r["keep"]) == 1:
                continue
            reason_prefix = r["reason"].split(":", 1)[0]
            if reason_prefix not in selected_reasons:
                continue
            src = ARCHIVE_DIR / sp / r["filename"]
            dst = DATASET_DIR  / sp / r["filename"]
            if not src.exists():
                skipped_missing += 1
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not args.dry_run:
                shutil.move(str(src), str(dst))
            moved += 1
            by_reason[reason_prefix] = by_reason.get(reason_prefix, 0) + 1

    # Final summary
    print(f"\n=== SUMMARY ===")
    print(f"  restored:        {moved}")
    print(f"  missing in archive (skipped): {skipped_missing}")
    if by_reason:
        for k, v in sorted(by_reason.items(), key=lambda x: -x[1]):
            print(f"  {k:<24} {v}")
    if args.dry_run:
        print("\n(DRY RUN — no files were moved.)")


if __name__ == "__main__":
    main()
