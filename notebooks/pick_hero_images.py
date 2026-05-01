"""
Hero Image Picker for the Species Catalogue
=========================================================
Scans dataset/raw/<species_key>/ and picks the best
representative image per species for the GUI catalogue
(`gui/static/img/species/<species_key>.jpg`).

Scoring criteria (combined into a single weighted score):
    - sharpness  : variance of the Laplacian (no-blur)
    - resolution : min(width, height), capped at 2000 px
    - aspect     : penalty for too-portrait or too-square
                   (3:2 landscape ideal)
    - central density:
                   ratio of high-frequency content in the central
                   60% of the image vs. the edges. Acts as a
                   crude "subject fills frame" proxy without
                   needing object detection.

Optional: --use-detector enables a torchvision Faster R-CNN
detector (COCO 'bird' class) that gives a true bbox-area score.
Slower (~1 s / image on CPU) but very accurate for the
"full body close-up" criterion.

Outputs:
    results/hero_candidates_<species>.jpg  (top-N contact sheet)
    results/hero_scores.csv                (full scoring table)
    gui/static/img/species/<species>.jpg   (the auto-pick, only with --apply)

Usage:
    # Just generate contact sheets so you can pick visually.
    python pick_hero_images.py

    # Auto-replace the catalogue images with the top-1 per species.
    python pick_hero_images.py --apply

    # Use the bird detector (slower but better for "close-up"):
    python pick_hero_images.py --use-detector --apply

    # Scan only one species.
    python pick_hero_images.py --species aquila_audax
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

# ─── Configuración ──────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset" / "raw"
GUI_OUT_DIR = BASE_DIR / "gui" / "static" / "img" / "species"
RESULTS_DIR = BASE_DIR / "results"

SPECIES_KEYS = [
    "aquila_audax", "circus_assimilis", "elanus_axillaris",
    "falco_cenchroides", "falco_peregrinus", "hieraaetus_morphnoides",
    "lophoictinia_isura", "tachyspiza_fasciata",
]

THUMB_SIZE         = (800, 540)        # final hero size — 3:2-ish, larger
CONTACT_THUMB      = (240, 160)        # candidate strip thumb size
CONTACT_TOP_N      = 6                 # candidates to show
MIN_DIM            = 800               # require ≥ 800 px on the short side
MAX_PER_SPECIES    = 80                # cap candidate evaluation cost

# Score weights (normalised features; sum doesn't need to be 1).
W_SHARP   = 0.25
W_RES     = 0.20
W_ASPECT  = 0.05
W_CENTER  = 0.15
W_DETECT  = 0.55                       # crank the bird-detector weight
                                       # so full-body shots dominate

# Ideal bird-bbox area as a fraction of the image. Below this the
# bird is too small (full-frame habitat shots); above this the crop
# is too tight (head/portraits). Used only with --use-detector.
IDEAL_AREA_LO  = 0.18
IDEAL_AREA_HI  = 0.65
IDEAL_AREA_PEAK = 0.40                 # peak score at ~40% area


# ─── Métricas ───────────────────────────────────────────
def laplacian_variance(gray: np.ndarray) -> float:
    """No-cv2 Laplacian variance — a classical sharpness proxy."""
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    pad = np.pad(gray.astype(np.float32), 1, mode="reflect")
    out = (
        k[0, 1] * pad[:-2, 1:-1] +
        k[1, 0] * pad[1:-1, :-2] +
        k[1, 1] * pad[1:-1, 1:-1] +
        k[1, 2] * pad[1:-1, 2:]  +
        k[2, 1] * pad[2:,  1:-1]
    )
    return float(out.var())


def aspect_score(w: int, h: int) -> float:
    """1.0 at 3:2 landscape; falls off as we move away from it."""
    if h == 0:
        return 0.0
    target = 1.5
    ratio  = w / h
    diff   = abs(ratio - target)
    return max(0.0, 1.0 - diff)        # 0 at ratio=0.5 or ratio=2.5


def central_density(gray: np.ndarray) -> float:
    """
    Ratio of Laplacian variance in the central 60% vs. the edges.
    > 1 means the subject is concentrated in the centre.
    """
    h, w = gray.shape
    cy0, cy1 = int(h * 0.20), int(h * 0.80)
    cx0, cx1 = int(w * 0.20), int(w * 0.80)
    centre = gray[cy0:cy1, cx0:cx1]

    edge_mask        = np.ones_like(gray, dtype=bool)
    edge_mask[cy0:cy1, cx0:cx1] = False
    edges            = gray[edge_mask]

    var_c = laplacian_variance(centre)
    var_e = float(edges.var()) + 1e-6
    return var_c / var_e


def load_grey(path: Path, max_dim: int = 600) -> np.ndarray | None:
    """Open + downscale to grey for fast metric computation."""
    try:
        img = Image.open(path).convert("RGB")
        img = ImageOps.exif_transpose(img)
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        return np.asarray(img.convert("L"), dtype=np.uint8)
    except Exception:
        return None


# ─── Detector opcional (torchvision) ────────────────────
_detector = None
def lazy_detector():
    global _detector
    if _detector is None:
        import torch
        from torchvision.models.detection import (
            fasterrcnn_resnet50_fpn, FasterRCNN_ResNet50_FPN_Weights
        )
        weights   = FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        _detector = fasterrcnn_resnet50_fpn(weights=weights, box_score_thresh=0.4)
        _detector.eval()
        _detector._ra_categories = weights.meta["categories"]
    return _detector


def _full_body_score(area_frac: float) -> float:
    """
    Triangular preference around IDEAL_AREA_PEAK.
    Returns 1.0 at the peak, 0.0 at the edges of [LO, HI].
    Encourages images where the bird occupies ~25–55% of frame —
    typical of a full-body shot rather than a tiny silhouette
    or a tight head close-up.
    """
    if area_frac < IDEAL_AREA_LO or area_frac > IDEAL_AREA_HI:
        return 0.0
    if area_frac <= IDEAL_AREA_PEAK:
        return (area_frac - IDEAL_AREA_LO) / (IDEAL_AREA_PEAK - IDEAL_AREA_LO)
    return (IDEAL_AREA_HI - area_frac) / (IDEAL_AREA_HI - IDEAL_AREA_PEAK)


def detect_bird_score(path: Path) -> float:
    """
    Detect the bird with Faster R-CNN and score the image based on:
    - bbox area in the ideal full-body range (peak at ~40%),
    - non-clipped at edges (no body parts cut off),
    - high detection confidence.
    Returns 0.0 if no bird found or the image is unsuitable.
    """
    import torch
    from torchvision.transforms.functional import to_tensor

    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    W, H = img.size
    if W < MIN_DIM or H < MIN_DIM:
        return 0.0

    det = lazy_detector()
    with torch.no_grad():
        out = det([to_tensor(img)])[0]

    cats = det._ra_categories
    best  = 0.0
    for i in range(len(out["labels"])):
        cat = cats[int(out["labels"][i])]
        sc  = float(out["scores"][i])
        if cat != "bird" or sc < 0.5:
            continue
        x0, y0, x1, y1 = [float(v) for v in out["boxes"][i]]
        bw, bh = (x1 - x0), (y1 - y0)
        area_frac = (bw * bh) / (W * H)
        # Edge clipping: 0 if box touches an edge, 1 if well inside.
        margin = 0.02 * min(W, H)         # 2% of short side
        clip = 1.0
        if x0 < margin or y0 < margin or x1 > W - margin or y1 > H - margin:
            clip = 0.55                   # heavy penalty for clipped birds
        body = _full_body_score(area_frac)
        # Prefer high-confidence detections only as tie-breaker
        score = body * clip * (0.7 + 0.3 * min(sc, 1.0))
        if score > best:
            best = score
    return best


# ─── Scoring de candidatos ──────────────────────────────
def score_image(path: Path, use_detector: bool) -> dict | None:
    """Compute a combined quality score for an image."""
    grey = load_grey(path)
    if grey is None:
        return None
    h, w = grey.shape

    # Hard filter: get the source dimensions (not the downscaled grey).
    try:
        src_w, src_h = Image.open(path).size
    except Exception:
        src_w, src_h = w, h
    if min(src_w, src_h) < MIN_DIM:
        # Too small to deliver a quality hero — skip outright.
        return None

    sharp  = laplacian_variance(grey)
    centre = central_density(grey)
    asp    = aspect_score(w, h)
    res    = min(w, h)

    sharp_n = min(sharp / 2000.0, 1.0)
    res_n   = min(res / 1500.0,   1.0)
    cen_n   = min(centre / 3.0,   1.0)

    score = (
        W_SHARP  * sharp_n +
        W_RES    * res_n   +
        W_ASPECT * asp     +
        W_CENTER * cen_n
    )

    detect = None
    if use_detector:
        try:
            detect = detect_bird_score(path)
            score += W_DETECT * min(detect, 1.0)
        except Exception as e:
            detect = -1.0
            print(f"  detector failed on {path.name}: {e}")

    return {
        "path":       str(path),
        "sharp":      sharp,
        "resolution": res,
        "aspect":     asp,
        "central":    centre,
        "detect":     detect if detect is not None else "",
        "score":      score,
    }


# ─── Contact sheet ──────────────────────────────────────
def build_contact_sheet(species_key: str, ranked: list[dict],
                        out_path: Path) -> None:
    """Render a horizontal strip of top candidates with overlays."""
    n = min(CONTACT_TOP_N, len(ranked))
    tw, th = CONTACT_THUMB
    pad = 8
    sheet = Image.new("RGB", (n * tw + (n + 1) * pad, th + 60),
                      (245, 246, 248))
    draw  = ImageDraw.Draw(sheet)

    try:
        font  = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
        font2 = ImageFont.truetype("DejaVuSans.ttf",      11)
    except Exception:
        font  = ImageFont.load_default()
        font2 = ImageFont.load_default()

    draw.text((pad, 8), f"{species_key} — top {n} candidates",
              fill=(40, 40, 40), font=font)

    for i, r in enumerate(ranked[:n]):
        try:
            im = Image.open(r["path"]).convert("RGB")
            im = ImageOps.exif_transpose(im)
            im = ImageOps.fit(im, (tw, th), method=Image.LANCZOS)
        except Exception:
            im = Image.new("RGB", (tw, th), (200, 200, 200))

        x = pad + i * (tw + pad)
        y = 32
        sheet.paste(im, (x, y))
        # Rank badge
        draw.rectangle([x, y, x + 30, y + 22], fill=(27, 79, 114))
        draw.text((x + 6, y + 4), f"#{i+1}",
                  fill="white", font=font)
        # Score line under thumb
        meta = (f"score {r['score']:.2f} | "
                f"sharp {r['sharp']:.0f} | "
                f"{r['resolution']} px")
        draw.text((x, y + th + 4), meta,
                  fill=(60, 60, 60), font=font2)

    sheet.save(out_path, format="JPEG", quality=85, optimize=True)


def write_hero(src_path: Path, dst_path: Path) -> None:
    img = Image.open(src_path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    thumb = ImageOps.fit(img, THUMB_SIZE, method=Image.LANCZOS,
                         centering=(0.5, 0.5))
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    thumb.save(dst_path, format="JPEG", quality=88, optimize=True,
               progressive=True)


# ─── Pipeline por especie ───────────────────────────────
def process_species(species_key: str, use_detector: bool,
                    apply_pick: bool) -> list[dict]:
    src_dir = DATASET_DIR / species_key
    files = (
        list(src_dir.glob("*.jpg")) +
        list(src_dir.glob("*.jpeg")) +
        list(src_dir.glob("*.png"))
    )
    if not files:
        print(f"\n[{species_key}] no images found in {src_dir}")
        return []

    print(f"\n[{species_key}] scanning {len(files)} images "
          f"(capped at {MAX_PER_SPECIES} for scoring)")

    # Pre-filter by file size (cheap proxy for resolution).
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    files = files[:MAX_PER_SPECIES]

    scored: list[dict] = []
    for i, p in enumerate(files):
        r = score_image(p, use_detector)
        if r is None:
            continue
        r["species"] = species_key
        scored.append(r)
        if (i + 1) % 20 == 0:
            print(f"  scored {i+1}/{len(files)}")

    scored.sort(key=lambda r: r["score"], reverse=True)

    if not scored:
        print(f"  no scored images for {species_key}")
        return []

    # Save contact sheet
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    sheet_path = RESULTS_DIR / f"hero_candidates_{species_key}.jpg"
    build_contact_sheet(species_key, scored, sheet_path)
    print(f"  contact sheet -> {sheet_path}")

    # Apply pick
    if apply_pick:
        pick = Path(scored[0]["path"])
        dst  = GUI_OUT_DIR / f"{species_key}.jpg"
        write_hero(pick, dst)
        print(f"  hero -> {dst}  (from {pick.name})")

    return scored


# ─── CLI ────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--species", default=None,
                   help="Limit to one species_key")
    p.add_argument("--apply", action="store_true",
                   help="Write the top-1 of each species into the GUI folder")
    p.add_argument("--use-detector", action="store_true",
                   help="Use torchvision Faster R-CNN to score 'bird in frame' (slower)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    keys = [args.species] if args.species else SPECIES_KEYS
    if args.species and args.species not in SPECIES_KEYS:
        raise SystemExit(f"Unknown species: {args.species}")

    print(f"Hero picker — apply={args.apply} | "
          f"detector={args.use_detector} | "
          f"species={keys}")

    all_rows: list[dict] = []
    for k in keys:
        rows = process_species(k, args.use_detector, args.apply)
        all_rows.extend(rows[:CONTACT_TOP_N])     # only log top-N per species

    # Dump scoring table
    if all_rows:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out = RESULTS_DIR / "hero_scores.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["species", "path", "score",
                          "sharp", "resolution", "aspect",
                          "central", "detect"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in all_rows:
                w.writerow({k: r.get(k, "") for k in fieldnames})
        print(f"\nScores table -> {out}")


if __name__ == "__main__":
    main()
