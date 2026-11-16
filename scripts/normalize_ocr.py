# -*- coding: utf-8 -*-
"""Normalize OCR text for 2025.06 papers: fullwidth->ASCII, strip watermarks, fix O/0."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "02-parsed"

FILES = [
    "2025.06六级真题第1套_raw.txt",
    "2025.06六级真题第2套_raw.txt",
    "2025.06六级真题第3套_raw.txt",
]

NOISE = re.compile(r"(公众号|语听颖想说|颖想说|请用黑色签字笔|准考证号|未得到监考教师指令|错填、未填)")


def normalize(text: str) -> str:
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("：", ":").replace("，", ", ")
    text = text.replace("''", '"').replace("'", "'")
    # OCR misreads O as 0 at option-letter positions
    text = re.sub(r"(?m)^0\)", "O)", text)
    text = re.sub(r"(?m)^([A-O]）)", lambda m: m.group(1).replace("）", ")"), text)
    lines = []
    for l in text.split("\n"):
        s = l.strip()
        if NOISE.search(s):
            # keep option/statement content if watermark appended inline
            s = NOISE.sub("", s).strip()
            if not s:
                continue
        lines.append(s)
    return "\n".join(lines)


def main():
    for f in FILES:
        p = SRC / f
        if not p.exists():
            print("skip", f)
            continue
        p.write_text(normalize(p.read_text(encoding="utf-8")), encoding="utf-8")
        print("normalized", f)


if __name__ == "__main__":
    main()
