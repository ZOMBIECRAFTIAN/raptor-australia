"""
Audit split leakage and near-duplicates in dataset/processed.

Checks:
- exact file duplicate hashes across train/val/test;
- perceptual near-duplicates across splits using dHash;
- filename/source ID reuse across splits;
- class counts by split.

Outputs:
- results/leakage_audit.json
- results/leakage_audit.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = BASE_DIR / "dataset" / "processed"
RESULTS_DIR = BASE_DIR / "results"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
SPLITS = ("train", "val", "test")


@dataclass(frozen=True)
class ImageRecord:
    split: str
    species: str
    path: Path
    rel_path: str
    sha256: str
    dhash: int
    source_id: str


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dhash(path: Path, hash_size: int = 8) -> int:
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img).convert("L")
        img = img.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())
    bits = []
    for row in range(hash_size):
        offset = row * (hash_size + 1)
        for col in range(hash_size):
            bits.append(1 if pixels[offset + col] > pixels[offset + col + 1] else 0)
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def source_id_from_name(path: Path) -> str:
    stem = path.stem.lower()
    if stem.startswith("ala_"):
        return stem
    uuid = re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        stem,
    )
    if uuid:
        return uuid.group(0)
    # iNaturalist-style names often end species_observation_photo.
    nums = re.findall(r"\d{6,}", stem)
    if nums:
        return "|".join(nums[-2:])
    return stem


def iter_images(dataset_dir: Path) -> list[ImageRecord]:
    records = []
    for split in SPLITS:
        split_dir = dataset_dir / split
        if not split_dir.exists():
            continue
        for species_dir in sorted(p for p in split_dir.iterdir() if p.is_dir()):
            for path in sorted(species_dir.iterdir()):
                if path.suffix.lower() not in IMAGE_EXTS or not path.is_file():
                    continue
                records.append(ImageRecord(
                    split=split,
                    species=species_dir.name,
                    path=path,
                    rel_path=path.relative_to(BASE_DIR).as_posix(),
                    sha256=file_sha256(path),
                    dhash=dhash(path),
                    source_id=source_id_from_name(path),
                ))
    return records


def cross_split_groups(records: list[ImageRecord], key: str) -> list[dict]:
    grouped = defaultdict(list)
    for rec in records:
        grouped[getattr(rec, key)].append(rec)

    out = []
    for value, items in grouped.items():
        splits = sorted({item.split for item in items})
        if len(splits) < 2:
            continue
        out.append({
            key: value,
            "splits": splits,
            "species": sorted({item.species for item in items}),
            "paths": [item.rel_path for item in items],
        })
    return sorted(out, key=lambda row: (row["splits"], row.get(key, "")))


def near_duplicate_pairs(records: list[ImageRecord], max_hamming: int) -> list[dict]:
    out = []
    sorted_records = sorted(records, key=lambda rec: rec.dhash)
    n = len(sorted_records)
    for i in range(n):
        a = sorted_records[i]
        for j in range(i + 1, n):
            b = sorted_records[j]
            if a.split == b.split:
                continue
            dist = hamming(a.dhash, b.dhash)
            if dist <= max_hamming:
                out.append({
                    "hamming": dist,
                    "a": a.rel_path,
                    "a_split": a.split,
                    "a_species": a.species,
                    "b": b.rel_path,
                    "b_split": b.split,
                    "b_species": b.species,
                })
    return sorted(out, key=lambda row: (row["hamming"], row["a"], row["b"]))


def counts_by_split(records: list[ImageRecord]) -> dict:
    counts = {split: defaultdict(int) for split in SPLITS}
    for rec in records:
        counts[rec.split][rec.species] += 1
    return {
        split: {"total": sum(species.values()), "species": dict(sorted(species.items()))}
        for split, species in counts.items()
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# Dataset Leakage Audit",
        "",
        f"Images audited: **{report['n_images']}**",
        f"Exact duplicate cross-split groups: **{report['n_exact_duplicate_groups']}**",
        f"Source-ID cross-split groups: **{report['n_source_id_groups']}**",
        f"Near-duplicate cross-split pairs: **{report['n_near_duplicate_pairs']}**",
        "",
        "## Interpretation",
        "",
    ]
    if report["passed"]:
        lines.append("No cross-split exact duplicates, source-ID reuse, or near-duplicates were detected at the configured threshold.")
    else:
        lines.append("Potential leakage was detected. Inspect the JSON report before using the split for final claims.")

    lines.extend(["", "## Split Counts", "", "| Split | Images |", "|---|---:|"])
    for split, info in report["counts_by_split"].items():
        lines.append(f"| {split} | {info['total']} |")

    if report["near_duplicate_pairs"]:
        lines.extend(["", "## First Near-Duplicate Pairs", "", "| Hamming | A | B |", "|---:|---|---|"])
        for row in report["near_duplicate_pairs"][:20]:
            lines.append(f"| {row['hamming']} | `{row['a']}` | `{row['b']}` |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_near_duplicate_contact_sheet(pairs: list[dict], out_path: Path,
                                       max_pairs: int = 13) -> None:
    if not pairs:
        return
    thumb_w, thumb_h = 220, 150
    label_h = 46
    pad = 10
    rows = min(max_pairs, len(pairs))
    sheet = Image.new(
        "RGB",
        (2 * thumb_w + 3 * pad, rows * (thumb_h + label_h + pad) + pad),
        (245, 246, 248),
    )
    draw = ImageDraw.Draw(sheet)
    for idx, pair in enumerate(pairs[:rows]):
        y = pad + idx * (thumb_h + label_h + pad)
        for col, key in enumerate(("a", "b")):
            path = BASE_DIR / pair[key]
            x = pad + col * (thumb_w + pad)
            try:
                img = Image.open(path).convert("RGB")
                img = ImageOps.exif_transpose(img)
                img = ImageOps.fit(img, (thumb_w, thumb_h), method=Image.Resampling.LANCZOS)
            except Exception:
                img = Image.new("RGB", (thumb_w, thumb_h), (200, 200, 200))
            sheet.paste(img, (x, y))
            label = f"{pair[f'{key}_split']} | {pair[f'{key}_species']}"
            draw.text((x, y + thumb_h + 4), label, fill=(20, 20, 20))
        draw.text(
            (pad, y + thumb_h + 22),
            f"dHash distance: {pair['hamming']}",
            fill=(120, 20, 20),
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=90)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", default=str(DATASET_DIR))
    parser.add_argument("--max-hamming", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.exists():
        raise SystemExit(f"Missing dataset directory: {dataset_dir}")

    records = iter_images(dataset_dir)
    exact = cross_split_groups(records, "sha256")
    source = cross_split_groups(records, "source_id")
    near = near_duplicate_pairs(records, args.max_hamming)

    report = {
        "dataset_dir": str(dataset_dir),
        "n_images": len(records),
        "max_hamming": args.max_hamming,
        "counts_by_split": counts_by_split(records),
        "exact_duplicate_groups": exact,
        "source_id_groups": source,
        "near_duplicate_pairs": near,
        "n_exact_duplicate_groups": len(exact),
        "n_source_id_groups": len(source),
        "n_near_duplicate_pairs": len(near),
        "passed": len(exact) == 0 and len(source) == 0 and len(near) == 0,
        "note": (
            "dHash near-duplicate checks are a screening tool, not a final "
            "manual visual audit. Photographer/event leakage requires richer "
            "metadata than filenames when not available locally."
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / "leakage_audit.json"
    out_md = RESULTS_DIR / "leakage_audit.md"
    out_sheet = RESULTS_DIR / "leakage_near_duplicate_pairs.jpg"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, out_md)
    build_near_duplicate_contact_sheet(near, out_sheet)

    print(json.dumps({
        "n_images": report["n_images"],
        "exact_duplicate_groups": report["n_exact_duplicate_groups"],
        "source_id_groups": report["n_source_id_groups"],
        "near_duplicate_pairs": report["n_near_duplicate_pairs"],
        "passed": report["passed"],
        "json": str(out_json),
        "markdown": str(out_md),
        "contact_sheet": str(out_sheet) if near else None,
    }, indent=2))


if __name__ == "__main__":
    main()
