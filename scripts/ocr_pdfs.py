# -*- coding: utf-8 -*-
"""OCR scanned CET-6 PDFs (image-only pages) into text files.

Renders pages at 200dpi via pymupdf, OCRs with RapidOCR, writes
02-parsed/<name>_raw.txt
"""
import sys
import time
from pathlib import Path

import pymupdf
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "01-papers"
OUT = ROOT / "02-parsed"

TARGETS = [
    # 2024.12: papers already have text layer; only解析 are scanned
    "2024.12英语六级解析第1套",
    "2024.12英语六级解析第2套",
    "2024.12英语六级解析第3套",
    # 2025.06: everything scanned
    "2025.06六级真题第1套",
    "2025.06六级真题第2套",
    "2025.06六级真题第3套",
    "2025.06英语六级解析第1套",
    "2025.06英语六级解析第2套",
    "2025.06英语六级解析第3套",
]


def ocr_pdf(name: str, ocr: RapidOCR) -> None:
    src = PAPERS / f"{name}.pdf"
    doc = pymupdf.open(src)
    parts = []
    t0 = time.time()
    for pno, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
        img_bytes = pix.tobytes("png")
        result, _ = ocr(img_bytes)
        lines = []
        if result:
            # result: [ [box, text, score], ... ] roughly top-to-bottom
            for item in result:
                text = item[1].strip()
                if text:
                    lines.append(text)
        parts.append("\n".join(lines))
        print(f"  page {pno}/{len(doc)} ({len(lines)} lines)", flush=True)
    text = "\n".join(parts)
    (OUT / f"{name}_raw.txt").write_text(text, encoding="utf-8")
    print(f"[OK] {name}: {len(doc)} pages, {len(text)} chars, {time.time()-t0:.0f}s")


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    ocr = RapidOCR()
    for name in TARGETS:
        if only and not any(o in name for o in only):
            continue
        print(f"== {name} ==", flush=True)
        ocr_pdf(name, ocr)


if __name__ == "__main__":
    main()
