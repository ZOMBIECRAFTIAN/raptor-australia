"""
Audit the exported thesis PDF.

This verifies the PDF without relying on a rasterizer. It checks page count,
extractable text, required thesis sections, core metrics and key project
concepts. Visual page inspection is still recommended when a PDF renderer is
available.
"""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = PROJECT_ROOT / "docs" / "Australian_Raptor_Thesis_v1_5.pdf"
RESULTS_PATH = PROJECT_ROOT / "results" / "thesis_pdf_audit.json"

REQUIRED_TEXT = [
    "Abstract",
    "Chapter 1. Introduction",
    "Chapter 2. Literature Review",
    "Chapter 3. Methodology",
    "Chapter 4. Results",
    "Chapter 5. Software",
    "Chapter 6. Discussion",
    "Appendix A. Dataset Datasheet Summary",
    "Appendix B. Model Card Summary",
    "Appendix E. Release Package",
    "Bibliography",
    "YOLO",
    "EfficientNetB4",
    "Darwin Core",
    "AUSLAN",
    "0.8495",
    "0.8482",
]


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(PDF_PATH)

    reader = PdfReader(str(PDF_PATH))
    pages = reader.pages
    extracted_text = "\n".join((page.extract_text() or "") for page in pages)
    missing_text = [token for token in REQUIRED_TEXT if token not in extracted_text]

    checks = {
        "pdf_exists": PDF_PATH.exists(),
        "pdf_size_gt_100kb": PDF_PATH.stat().st_size > 100_000,
        "page_count_gt_8": len(pages) > 8,
        "extractable_text_gt_5000_chars": len(extracted_text) > 5_000,
        "required_text_present": not missing_text,
    }
    report = {
        "pdf_path": str(PDF_PATH),
        "file_size_bytes": PDF_PATH.stat().st_size,
        "page_count": len(pages),
        "metadata": {str(k): str(v) for k, v in (reader.metadata or {}).items()},
        "text_characters": len(extracted_text),
        "missing_text": missing_text,
        "checks": checks,
        "passed": all(checks.values()),
        "note": (
            "Text/PDF structural audit only. Visual page QA requires a "
            "rasterizer such as LibreOffice, Poppler, Ghostscript or "
            "ImageMagick."
        ),
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
