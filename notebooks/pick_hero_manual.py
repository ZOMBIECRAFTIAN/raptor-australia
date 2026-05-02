"""
Manual Hero Image Picker — interactive Tk GUI
=========================================================
Shows the top-12 candidate images per species side-by-side as a
3×4 thumbnail grid. You click your preferred image; the script
copies it to ``gui/static/img/species/<species_key>.jpg``.

Use this when the automatic picker (``pick_hero_images.py
--use-detector``) keeps surfacing photos of feathers, dead
specimens, captive birds, or distant habitat shots — situations
the heuristics cannot reliably distinguish from a good portrait.

Why a UI instead of more rules?
- 8 species × ~10 seconds of human judgment = under two minutes
  total, with results far better than any heuristic.
- Saves curator time vs. browsing in File Explorer.

Usage (from project root, requires ``raptor_env`` active):
    python notebooks/pick_hero_manual.py
    python notebooks/pick_hero_manual.py --species aquila_audax
    python notebooks/pick_hero_manual.py --top 18

Controls inside the window:
    Click any thumbnail   → that image becomes the new hero
    Skip button           → keep the current hero unchanged
    Quit / X              → cancel session

Outputs:
    gui/static/img/species/<species_key>.jpg  (overwritten)
    results/hero_picks_manual.csv             (audit log)
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from PIL import Image, ImageOps, ImageTk

# ─── Configuration ──────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset" / "raw"
GUI_OUT_DIR = BASE_DIR / "gui" / "static" / "img" / "species"
RESULTS_DIR = BASE_DIR / "results"
LOG_PATH    = RESULTS_DIR / "hero_picks_manual.csv"

THUMB_SIZE     = (240, 180)      # grid thumbnail size
HERO_SIZE      = (640, 426)      # final hero size (matches ALA src)
MIN_DIM        = 480
DEFAULT_TOP_N  = 12              # 4×3 grid

SPECIES_LABELS = {
    "aquila_audax":           "Wedge-tailed Eagle",
    "circus_assimilis":       "Spotted Harrier",
    "elanus_axillaris":       "Black-shouldered Kite",
    "falco_cenchroides":      "Nankeen Kestrel",
    "falco_peregrinus":       "Peregrine Falcon",
    "hieraaetus_morphnoides": "Little Eagle",
    "lophoictinia_isura":     "Square-tailed Kite",
    "tachyspiza_fasciata":    "Brown Goshawk",
}


# ─── Candidate ranking (fast heuristic, no detector) ────
def laplacian_variance(gray: np.ndarray) -> float:
    """Sharpness proxy — higher = sharper."""
    pad = np.pad(gray.astype(np.float32), 1, mode="reflect")
    out = (pad[:-2, 1:-1] + pad[1:-1, :-2] +
           pad[1:-1, 2:] + pad[2:, 1:-1] - 4 * pad[1:-1, 1:-1])
    return float(out.var())


def score_image(path: Path) -> float | None:
    """Return a quick quality score; None if unusable."""
    try:
        img = Image.open(path).convert("RGB")
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        if min(w, h) < MIN_DIM:
            return None
        thumb = img.copy()
        thumb.thumbnail((600, 600), Image.LANCZOS)
        gray = np.asarray(thumb.convert("L"))
        sharp = laplacian_variance(gray)
        # Normalise resolution + sharpness into a single score.
        return min(sharp / 2500.0, 1.0) + min(min(w, h) / 1500.0, 1.0)
    except Exception:
        return None


def top_candidates(species_key: str, top_n: int) -> list[Path]:
    folder = DATASET_DIR / species_key
    files = (list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) +
             list(folder.glob("*.png")))
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    files = files[: top_n * 4]   # cap evaluation
    scored: list[tuple[float, Path]] = []
    for p in files:
        s = score_image(p)
        if s is not None:
            scored.append((s, p))
    scored.sort(reverse=True, key=lambda t: t[0])
    return [p for _, p in scored[:top_n]]


# ─── Apply pick (writes the hero JPG) ───────────────────
def apply_pick(src: Path, species_key: str) -> Path:
    img = Image.open(src).convert("RGB")
    img = ImageOps.exif_transpose(img)
    thumb = ImageOps.fit(img, HERO_SIZE, method=Image.LANCZOS,
                         centering=(0.5, 0.5))
    GUI_OUT_DIR.mkdir(parents=True, exist_ok=True)
    dst = GUI_OUT_DIR / f"{species_key}.jpg"
    thumb.save(dst, format="JPEG", quality=90, optimize=True,
               progressive=True)
    return dst


def log_pick(species_key: str, src: Path | None, action: str) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fresh = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if fresh:
            w.writerow(["timestamp", "species_key", "action", "source"])
        w.writerow([
            datetime.now().isoformat(timespec="seconds"),
            species_key, action, str(src or ""),
        ])


# ─── Tk GUI ─────────────────────────────────────────────
class PickerApp(tk.Tk):
    def __init__(self, species_keys: list[str], top_n: int):
        super().__init__()
        self.species_keys = species_keys
        self.top_n        = top_n
        self.idx          = 0
        self.candidates: list[Path] = []
        self.thumb_imgs:  list[ImageTk.PhotoImage] = []   # keep refs

        self.title("Australian Raptor — Manual Hero Picker")
        self.geometry("1100x780")
        self.configure(bg="#f4f6f8")

        # Header
        header = tk.Frame(self, bg="#1B4F72", height=72)
        header.pack(fill="x")
        self.title_label = tk.Label(
            header, text="", bg="#1B4F72", fg="white",
            font=("Segoe UI", 16, "bold"))
        self.title_label.pack(side="left", padx=20, pady=18)
        self.progress_label = tk.Label(
            header, text="", bg="#1B4F72", fg="#cfd8e3",
            font=("Segoe UI", 11))
        self.progress_label.pack(side="right", padx=20, pady=20)

        # Status bar (current hero)
        self.status = tk.Label(
            self, text="Loading…", bg="#f4f6f8", fg="#555",
            font=("Segoe UI", 10), justify="left", anchor="w")
        self.status.pack(fill="x", padx=20, pady=(8, 0))

        # Grid container
        self.grid_frame = tk.Frame(self, bg="#f4f6f8")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=12)

        # Footer buttons
        footer = tk.Frame(self, bg="#f4f6f8")
        footer.pack(fill="x", pady=(0, 12))
        ttk.Button(footer, text="Skip — keep current",
                   command=self.skip).pack(side="left", padx=20)
        ttk.Button(footer, text="Quit",
                   command=self.destroy).pack(side="right", padx=20)

        self.after(80, self.load_species)

    # ── per-species ──────────────────────────────────────
    def load_species(self) -> None:
        if self.idx >= len(self.species_keys):
            messagebox.showinfo("Done",
                                f"Reviewed {len(self.species_keys)} species. "
                                f"Audit log → {LOG_PATH}")
            self.destroy()
            return
        sp_key = self.species_keys[self.idx]
        self.title_label.config(
            text=f"{SPECIES_LABELS.get(sp_key, sp_key)}  ({sp_key})")
        self.progress_label.config(
            text=f"Species {self.idx + 1} of {len(self.species_keys)}")
        current_hero = GUI_OUT_DIR / f"{sp_key}.jpg"
        self.status.config(
            text=f"Current hero: {current_hero.name} "
                 f"({current_hero.stat().st_size if current_hero.exists() else 0} bytes)  "
                 f"·  Click a thumbnail to replace it, or press Skip.")
        self.update_idletasks()

        # Clear previous grid
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.thumb_imgs.clear()

        self.candidates = top_candidates(sp_key, self.top_n)
        if not self.candidates:
            messagebox.showwarning(
                "No candidates",
                f"{sp_key}: no usable images of "
                f"min-dim ≥ {MIN_DIM}px. Skipping.")
            self.skip()
            return

        cols = 4
        for i, path in enumerate(self.candidates):
            row, col = divmod(i, cols)
            im = Image.open(path).convert("RGB")
            im = ImageOps.exif_transpose(im)
            im = ImageOps.fit(im, THUMB_SIZE, method=Image.LANCZOS)
            ph = ImageTk.PhotoImage(im)
            self.thumb_imgs.append(ph)

            tile = tk.Frame(self.grid_frame, bg="white",
                            highlightthickness=2,
                            highlightbackground="#dbe2ea",
                            cursor="hand2")
            tile.grid(row=row, column=col, padx=8, pady=8)
            label = tk.Label(tile, image=ph, bg="white", cursor="hand2")
            label.pack()
            num = tk.Label(tile, text=f"#{i+1}  ·  {path.name[:34]}",
                           bg="white", fg="#1B4F72",
                           font=("Segoe UI", 9, "bold"),
                           cursor="hand2")
            num.pack(pady=(0, 4))
            for widget in (tile, label, num):
                widget.bind("<Button-1>",
                            lambda _e, p=path, k=sp_key: self.choose(p, k))
                widget.bind("<Enter>",
                            lambda _e, t=tile: t.config(
                                highlightbackground="#1A7C6E"))
                widget.bind("<Leave>",
                            lambda _e, t=tile: t.config(
                                highlightbackground="#dbe2ea"))

    # ── actions ──────────────────────────────────────────
    def choose(self, src: Path, species_key: str) -> None:
        try:
            dst = apply_pick(src, species_key)
            log_pick(species_key, src, "applied")
            print(f"  ✓ {species_key} → {src.name}  ({dst})")
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Could not apply pick for {species_key}: {e}")
            return
        self.idx += 1
        self.load_species()

    def skip(self) -> None:
        sp_key = self.species_keys[self.idx]
        log_pick(sp_key, None, "skipped")
        print(f"  ⊘ {sp_key} skipped (kept current hero)")
        self.idx += 1
        self.load_species()


# ─── CLI ────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--species", default=None,
                   help="Limit to one species_key")
    p.add_argument("--top", type=int, default=DEFAULT_TOP_N,
                   help=f"Candidates per species (default {DEFAULT_TOP_N})")
    return p.parse_args()


def main():
    args = parse_args()
    if args.species:
        keys = [args.species]
    else:
        keys = list(SPECIES_LABELS.keys())

    print("Australian Raptor — Manual Hero Picker")
    print(f"Reviewing {len(keys)} species, {args.top} candidates each")
    app = PickerApp(keys, args.top)
    app.mainloop()


if __name__ == "__main__":
    main()
