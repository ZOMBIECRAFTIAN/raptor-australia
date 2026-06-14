"""
AUSLAN Sign Animation Generator
=========================================================
Creates 8 schematic SVG animations (one per species) that
illustrate the proposed AUSLAN sign motion for each raptor.

These are PROVISIONAL placeholder illustrations of the
sign pattern, NOT validated AUSLAN signs. Real videos
will replace them after consultation with the Deaf
Society of NSW / RIDBC (see docs/auslan_consultation/).

Output:
    gui/static/auslan_videos/<species_key>.svg

Each SVG contains:
- Hero label (common + scientific name)
- Animated motion path (per-species pattern)
- One or two animated hand markers tracing the path
- Caption with the textual sign description
- Looping animation via SMIL

Usage:
    python generate_auslan_svgs.py
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
OUTPUT_DIR  = BASE_DIR / "gui" / "static" / "auslan_videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Per-species sign motion specs ──────────────────────
# Each entry encodes:
#   common_name, scientific_name, color, description,
#   motion: kind, paths (list of d= attrs), duration_s, hand_count
SIGNS: list[dict] = [
    {
        "key":    "aquila_audax",
        "common": "Wedge-tailed Eagle",
        "sci":    "Aquila audax",
        "color":  "#2C3E50",
        "desc":   "Both hands in inverted V, extend "
                  "downward with wide amplitude",
        "kind":   "double-spread",
        "paths":  ["M 240,90 L 100,260", "M 240,90 L 380,260"],
        "dur":    "2.4s",
    },
    {
        "key":    "falco_peregrinus",
        "common": "Peregrine Falcon",
        "sci":    "Falco peregrinus",
        "color":  "#8E44AD",
        "desc":   "Dominant hand index finger, rapid "
                  "vertical dive downward",
        "kind":   "single",
        "paths":  ["M 240,80 L 240,280"],
        "dur":    "0.9s",
    },
    {
        "key":    "circus_assimilis",
        "common": "Spotted Harrier",
        "sci":    "Circus assimilis",
        "color":  "#27AE60",
        "desc":   "Both flat hands, lateral oscillating "
                  "glide at low height",
        "kind":   "double-oscillate",
        "paths":  [
            "M 80,250 Q 160,210 240,250 T 400,250",
            "M 80,260 Q 160,220 240,260 T 400,260",
        ],
        "dur":    "3.0s",
    },
    {
        "key":    "tachyspiza_fasciata",
        "common": "Brown Goshawk",
        "sci":    "Tachyspiza fasciata",
        "color":  "#D35400",
        "desc":   "Curved hand, rapid zigzag movement "
                  "between trees",
        "kind":   "single",
        "paths":  [
            "M 80,200 L 160,140 L 240,200 L 320,140 L 400,200",
        ],
        "dur":    "1.6s",
    },
    {
        "key":    "falco_cenchroides",
        "common": "Nankeen Kestrel",
        "sci":    "Falco cenchroides",
        "color":  "#E67E22",
        "desc":   "Open hand, stationary vibration "
                  "(hovering motion)",
        "kind":   "single-vibrate",
        "paths":  [
            "M 240,200 m -8,0 a 8,4 0 1,0 16,0 a 8,4 0 1,0 -16,0",
        ],
        "dur":    "0.5s",
    },
    {
        "key":    "elanus_axillaris",
        "common": "Black-shouldered Kite",
        "sci":    "Elanus axillaris",
        "color":  "#2980B9",
        "desc":   "Both hands in H, hover then short descent",
        "kind":   "double-hover-descend",
        "paths":  [
            "M 200,160 L 200,160 L 200,160 L 200,260",
            "M 280,160 L 280,160 L 280,160 L 280,260",
        ],
        "dur":    "2.6s",
    },
    {
        "key":    "lophoictinia_isura",
        "common": "Square-tailed Kite",
        "sci":    "Lophoictinia isura",
        "color":  "#16A085",
        "desc":   "Flat hand, slow glide with square "
                  "tail demarcated",
        "kind":   "single",
        "paths":  ["M 80,200 Q 240,170 400,200"],
        "dur":    "3.2s",
    },
    {
        "key":    "hieraaetus_morphnoides",
        "common": "Little Eagle",
        "sci":    "Hieraaetus morphnoides",
        "color":  "#C0392B",
        "desc":   "Compact hand, small active movement "
                  "(small size + broad wings)",
        "kind":   "single",
        "paths":  [
            "M 240,180 q -30,-25 0,-50 q 30,25 60,0 q -30,25 -60,50 z",
        ],
        "dur":    "1.8s",
    },
    {
        "key":    "falco_berigora",
        "common": "Brown Falcon",
        "sci":    "Falco berigora",
        "color":  "#A04000",
        "desc":   "Loose hand, broad lazy circular flight "
                  "(slow soaring falcon)",
        "kind":   "single",
        "paths":  [
            "M 240,200 m -80,0 a 80,50 0 1,0 160,0 a 80,50 0 1,0 -160,0",
        ],
        "dur":    "3.4s",
    },
    {
        "key":    "haliaeetus_leucogaster",
        "common": "White-bellied Sea-Eagle",
        "sci":    "Haliaeetus leucogaster",
        "color":  "#1F618D",
        "desc":   "Both flat hands, wide steady glide "
                  "above ocean surface",
        "kind":   "double-spread",
        "paths":  [
            "M 60,210 Q 240,180 420,210",
            "M 60,240 Q 240,260 420,240",
        ],
        "dur":    "3.6s",
    },
    {
        "key":    "haliastur_indus",
        "common": "Brahminy Kite",
        "sci":    "Haliastur indus",
        "color":  "#7B241C",
        "desc":   "Curved hand, smooth arc with brief "
                  "pause (coastal scavenging swoop)",
        "kind":   "single",
        "paths":  [
            "M 80,140 Q 240,40 400,140 Q 240,260 80,140",
        ],
        "dur":    "2.8s",
    },
    {
        "key":    "haliastur_sphenurus",
        "common": "Whistling Kite",
        "sci":    "Haliastur sphenurus",
        "color":  "#B7950B",
        "desc":   "Index finger drawn upward in long "
                  "curve (mimicking ascending whistle)",
        "kind":   "single",
        "paths":  [
            "M 100,280 Q 200,200 240,160 Q 280,120 380,80",
        ],
        "dur":    "2.2s",
    },
    {
        "key":    "milvus_migrans",
        "common": "Black Kite",
        "sci":    "Milvus migrans",
        "color":  "#34495E",
        "desc":   "Forked-V hand, tail flick side-to-side "
                  "(diagnostic forked tail)",
        "kind":   "single",
        "paths":  [
            "M 240,200 L 160,160 L 240,200 L 320,160 "
            "L 240,200 L 160,240 L 240,200 L 320,240",
        ],
        "dur":    "2.0s",
    },
    {
        "key":    "tachyspiza_novaehollandiae",
        "common": "Grey Goshawk",
        "sci":    "Tachyspiza novaehollandiae",
        "color":  "#7F8C8D",
        "desc":   "Open pale hand, silent forward glide "
                  "through dense forest",
        "kind":   "single",
        "paths":  [
            "M 60,200 L 200,180 L 280,220 L 420,200",
        ],
        "dur":    "2.4s",
    },
]


# ─── SVG template ───────────────────────────────────────
def render_svg(spec: dict) -> str:
    color    = spec["color"]
    paths    = spec["paths"]
    dur      = spec["dur"]
    common   = spec["common"]
    sci      = spec["sci"]
    desc     = spec["desc"]

    # Visible motion path(s) — dashed guideline
    guides = "\n".join(
        f'  <path d="{p}" stroke="rgba(255,255,255,0.35)" '
        f'stroke-width="2" stroke-dasharray="4 4" fill="none" />'
        for p in paths
    )

    # Animated hand markers (one per path)
    markers: list[str] = []
    for i, p in enumerate(paths):
        delay = "0s" if i == 0 else f"{i * 0.15:.2f}s"
        markers.append(
            f'  <g>\n'
            f'    <circle r="14" fill="white" />\n'
            f'    <text y="6" text-anchor="middle" '
            f'font-family="Segoe UI Emoji,Apple Color Emoji,sans-serif" '
            f'font-size="22">🤟</text>\n'
            f'    <animateMotion dur="{dur}" repeatCount="indefinite" '
            f'begin="{delay}" path="{p}" />\n'
            f'  </g>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 360"
     preserveAspectRatio="xMidYMid meet"
     role="img"
     aria-label="AUSLAN sign motion — {common}">

  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="{color}" />
      <stop offset="100%" stop-color="{color}DD" />
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="480" height="360" fill="url(#bg)" />

  <!-- Header -->
  <text x="240" y="40" text-anchor="middle" fill="white"
        font-family="Segoe UI, Arial, sans-serif"
        font-size="20" font-weight="700">
    {common}
  </text>
  <text x="240" y="62" text-anchor="middle" fill="rgba(255,255,255,0.78)"
        font-family="Segoe UI, Arial, sans-serif"
        font-style="italic" font-size="13">
    {sci}
  </text>

  <!-- Motion guideline -->
{guides}

  <!-- Animated hand marker(s) -->
{chr(10).join(markers)}

  <!-- Caption -->
  <rect x="0" y="312" width="480" height="48"
        fill="rgba(0,0,0,0.32)" />
  <text x="240" y="335" text-anchor="middle" fill="white"
        font-family="Segoe UI, Arial, sans-serif"
        font-size="13">
    {desc}
  </text>
  <text x="240" y="352" text-anchor="middle"
        fill="rgba(255,255,255,0.65)"
        font-family="Segoe UI, Arial, sans-serif"
        font-size="10" font-style="italic">
    PROVISIONAL ILLUSTRATION — pending Deaf community validation
  </text>
</svg>
'''


def main() -> None:
    print(f"Generating AUSLAN SVGs into {OUTPUT_DIR}")
    for spec in SIGNS:
        out = OUTPUT_DIR / f"{spec['key']}.svg"
        out.write_text(render_svg(spec), encoding="utf-8")
        print(f"  {out.name}  ({out.stat().st_size} B)")
    print(f"\nDone. {len(SIGNS)} files written.")


if __name__ == "__main__":
    main()
