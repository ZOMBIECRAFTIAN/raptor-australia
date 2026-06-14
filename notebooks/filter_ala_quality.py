"""
Quality filter for the raw image dataset (pre-training)
=========================================================
Walks every species folder under ``dataset/raw/`` and decides,
for each image, whether it is suitable for training. Images that
fail the filter are MOVED into ``dataset/raw_archive/<species>/``
(originals preserved — nothing is deleted).

Heuristics (fast, no external models — YOLO optional):

    1. Image opens cleanly                              [hard fail]
    2. min(width, height) ≥ MIN_DIM                     [hard fail]
    3. Aspect ratio between 0.45 and 2.2                [excludes
       museum trays, thin specimen plates]
    4. With --use-detector:
       a) at least one COCO 'bird' detection ≥ conf.   [hard fail]
       b) bird bbox area in [BBOX_MIN, BBOX_MAX] frame  [excludes
          habitat shots and tight feather close-ups]
       c) bbox not clipped at the frame edge            [excludes
          partial body shots, including most "specimen on tray"
          photos where the bird touches the edges]

The script writes:
    dataset/raw_archive/<species>/<file>.jpg          (filtered out)
    dataset/metadata/quality_filter.csv                (audit log)
    dataset/metadata/quality_summary.txt               (human-readable summary)

Usage (from project root):
    python notebooks/filter_ala_quality.py --dry-run
    python notebooks/filter_ala_quality.py --use-detector
    python notebooks/filter_ala_quality.py --species aquila_audax --use-detector

Recommended workflow:
    1. python notebooks/filter_ala_quality.py --dry-run --use-detector
       → review the proposed deletions
    2. python notebooks/filter_ala_quality.py --use-detector
       → archive the failures
    3. python notebooks/retrain.py
       → retrain on the cleaner dataset

If the model afterwards mis-classifies a particular species,
inspect dataset/raw_archive/<species>/ — false positives can be
moved back to dataset/raw/<species>/ and the cycle repeated.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
from datetime import datetime
from pathlib import Path
import sys
from typing import Iterable

from PIL import Image, ImageOps

# ─── Configuration ──────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
DATASET_DIR  = BASE_DIR / "dataset" / "raw"
ARCHIVE_DIR  = BASE_DIR / "dataset" / "raw_archive"
METADATA_DIR = BASE_DIR / "dataset" / "metadata"

MIN_DIM      = 160         # Lowered from 224 after the v1.2 filter run
                           # archived 88% of the dataset — many ALA &
                           # iNat images come in at 200-300px on the
                           # short side and are still usable when
                           # up-scaled to 380px for EfficientNetB4.
                           # Below 160px the up-scaling artefacts hurt
                           # more than they help.
ASPECT_LO    = 0.45
ASPECT_HI    = 2.20
BBOX_MIN     = 0.08        # 8% of frame — excludes habitat shots
BBOX_MAX     = 0.85        # 85% of frame — excludes tight head close-ups
DETECT_CONF  = 0.45        # confidence threshold for the 'bird' class
EDGE_MARGIN  = 0.015       # 1.5% of short side — clip-detection slack

GUI_DIR = BASE_DIR / "gui"
if str(GUI_DIR) not in sys.path:
    sys.path.insert(0, str(GUI_DIR))

# ─── YOLO detector (loaded only with --use-detector) ────
_detector = None


def yolo_weights_path() -> str:
    configured = os.environ.get("RAPTOR_YOLO_WEIGHTS")
    if configured:
        return configured
    local = BASE_DIR / "models" / "yolov8n.pt"
    return str(local) if local.exists() else "yolov8n.pt"


def lazy_detector():
    """Lazy-load YOLO once. Same detector family as the v1.5 app."""
    global _detector
    if _detector is None:
        from yolo_detector import YoloBirdDetector

        _detector = YoloBirdDetector(yolo_weights_path(),
                                     confidence=DETECT_CONF)
    return _detector


def detect_bird(path: Path) -> dict:
    """Return the best bird detection on the image, or {}."""
    det = lazy_detector()

    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    W, H = img.size

    best = {}
    best_score = 0.0
    for box in det.detect(img):
        sc = float(box.confidence)
        if sc < DETECT_CONF or sc <= best_score:
            continue
        x0, y0, x1, y1 = [float(v) for v in box.bbox]
        best = {
            "score": sc,
            "x0": x0, "y0": y0, "x1": x1, "y1": y1,
            "W": W, "H": H,
        }
        best_score = sc
    return best


# ─── Per-image classification ───────────────────────────
def classify(path: Path, use_detector: bool) -> tuple[bool, str]:
    """
    Return (keep, reason). reason is a short tag for the audit log.
    """
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            w, h = im.size
    except Exception as e:
        return False, f"corrupt:{type(e).__name__}"

    if min(w, h) < MIN_DIM:
        return False, f"too_small:{w}x{h}"

    aspect = w / max(1, h)
    if aspect < ASPECT_LO or aspect > ASPECT_HI:
        return False, f"aspect:{aspect:.2f}"

    if not use_detector:
        return True, "ok:fast"

    try:
        det = detect_bird(path)
    except Exception as e:
        return False, f"detector_error:{type(e).__name__}"

    if not det:
        return False, "no_bird_detected"

    bw = det["x1"] - det["x0"]
    bh = det["y1"] - det["y0"]
    area_frac = (bw * bh) / max(1, det["W"] * det["H"])
    if area_frac < BBOX_MIN:
        return False, f"too_small_bird:{area_frac:.2f}"
    if area_frac > BBOX_MAX:
        return False, f"too_close_up:{area_frac:.2f}"

    margin_px = EDGE_MARGIN * min(det["W"], det["H"])
    if (det["x0"] < margin_px or det["y0"] < margin_px or
            det["x1"] > det["W"] - margin_px or
            det["y1"] > det["H"] - margin_px):
        return False, "bbox_clipped_at_edge"

    return True, f"ok:bbox_area={area_frac:.2f}"


# ─── Pipeline ───────────────────────────────────────────
def run(species_filter: str | None, use_detector: bool, dry_run: bool):
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    log_path = METADATA_DIR / "quality_filter.csv"
    summary  = METADATA_DIR / "quality_summary.txt"

    species_keys = sorted(p.name for p in DATASET_DIR.iterdir()
                          if p.is_dir())
    if species_filter:
        if species_filter not in species_keys:
            raise SystemExit(f"Unknown species: {species_filter}")
        species_keys = [species_filter]

    print(f"\nQuality filter — detector: {use_detector} · "
          f"dry_run: {dry_run}")
    print(f"DATASET_DIR = {DATASET_DIR}")
    print(f"ARCHIVE_DIR = {ARCHIVE_DIR}\n")

    total_kept, total_removed = 0, 0
    by_reason: dict[str, int] = {}
    rows: list[dict] = []

    for sp in species_keys:
        files = sorted(p for p in (DATASET_DIR / sp).iterdir()
                       if p.is_file())
        kept, removed = 0, 0
        print(f"  [{sp:<28}] {len(files):>4} images …")
        for i, p in enumerate(files, 1):
            keep, reason = classify(p, use_detector)
            rows.append({
                "species_key": sp,
                "filename":    p.name,
                "keep":        int(keep),
                "reason":      reason,
            })
            if keep:
                kept += 1
            else:
                removed += 1
                by_reason[reason.split(":", 1)[0]] = (
                    by_reason.get(reason.split(":", 1)[0], 0) + 1)
                if not dry_run:
                    dest_dir = ARCHIVE_DIR / sp
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(p), str(dest_dir / p.name))

            if i % 100 == 0:
                print(f"      processed {i}/{len(files)} "
                      f"({kept} kept, {removed} archived)")

        total_kept    += kept
        total_removed += removed
        print(f"      → {kept} kept, {removed} archived "
              f"({100 * removed / max(1, len(files)):.0f}% filtered out)")

    # Audit log
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["species_key", "filename",
                                          "keep", "reason"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nAudit log → {log_path}")

    # Human-readable summary
    with open(summary, "w", encoding="utf-8") as f:
        f.write(f"Quality filter run — {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Detector: {use_detector} · Dry run: {dry_run}\n\n")
        f.write(f"Total kept:     {total_kept}\n")
        f.write(f"Total archived: {total_removed}\n\n")
        f.write("Removals by reason:\n")
        for reason, n in sorted(by_reason.items(),
                                 key=lambda x: -x[1]):
            f.write(f"  {reason:<24} {n}\n")
    print(f"Summary   → {summary}\n")

    print(f"=== SUMMARY ===")
    print(f"  kept:     {total_kept}")
    print(f"  archived: {total_removed}")
    if by_reason:
        print(f"  reasons:")
        for reason, n in sorted(by_reason.items(), key=lambda x: -x[1]):
            print(f"    {reason:<24} {n}")
    if dry_run:
        print(f"\n(DRY RUN — no files were moved.)")


# ─── CLI ────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--species", default=None,
                   help="Limit to one species_key")
    p.add_argument("--use-detector", action="store_true",
                   help="Use YOLO bird detection (slower, but catches "
                        "dead specimens, feathers, habitat shots)")
    p.add_argument("--dry-run", action="store_true",
                   help="Just report; don't move any files")
    return p.parse_args()


def main():
    args = parse_args()
    run(args.species, args.use_detector, args.dry_run)


if __name__ == "__main__":
    main()
