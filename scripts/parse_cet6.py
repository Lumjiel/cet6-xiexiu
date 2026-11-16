# -*- coding: utf-8 -*-
"""Parse CET-6 reading sections (A/B/C) from 2025.12 & 2026.06 papers into JSON.

Input : 02-parsed/<set>_raw.txt  (paper)  +  <set>_ans_raw.txt  (answers)
Output: 02-parsed/parsed/<set>.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "02-parsed"

SETS = {
    "cet6_2024_12_1": ("2024.12六级真题第1套_raw.txt", "nju_2024.12_解析第1套_raw.txt"),
    "cet6_2024_12_2": ("2024.12六级真题第2套_raw.txt", "nju_2024.12_解析第2套_raw.txt"),
    "cet6_2024_12_3": ("2024.12六级真题第3套_raw.txt", "nju_2024.12_解析第3套_raw.txt"),
    "cet6_2025_06_1": ("2025.06六级真题第1套_raw.txt", "cet6_2025_06_1_ans_raw.txt"),
    "cet6_2025_06_2": ("2025.06六级真题第2套_raw.txt", "cet6_2025_06_2_ans_raw.txt"),
    "cet6_2025_06_3": ("2025.06六级真题第3套_raw.txt", "cet6_2025_06_3_ans_raw.txt"),
    "cet6_2025_12_1": ("cet6_2025_12_1_raw.txt", "cet6_2025_12_1_ans_raw.txt"),    "cet6_2025_12_2": ("cet6_2025_12_2_raw.txt", "cet6_2025_12_2_ans_raw.txt"),
    "cet6_2025_12_3": ("cet6_2025_12_3_raw.txt", "cet6_2025_12_3_ans_raw.txt"),
    "cet6_2026_06_1": ("cet6_2026_06_1_raw.txt", "cet6_2026_06_1_ans_raw.txt"),
    "cet6_2026_06_2": ("cet6_2026_06_2_raw.txt", "cet6_2026_06_2_ans_raw.txt"),
    "cet6_2026_06_3": ("cet6_2026_06_3_raw.txt", "cet6_2026_06_3_ans_raw.txt"),
}


def clean(text: str) -> list[str]:
    return [l.strip() for l in text.split("\n")]


def reading_part(lines: list[str]) -> list[str]:
    """Keep only lines after the Part III reading marker (may span 2-3 lines)."""
    for i, l in enumerate(lines):
        if re.search(r"Part III", l):
            # 'Reading Comprehension' may be on the same line or one of the next lines
            window = " ".join(lines[i:i + 4])
            if re.search(r"Reading", window):
                return lines[i:]
    # OCR fallback: a standalone 'Reading Comprehension' header line
    for i, l in enumerate(lines):
        if re.fullmatch(r"Reading Comprehension", l):
            return lines[i:]
    return lines


def extract_answers(ans_lines: list[str]) -> dict[int, str]:
    """Answer key format: '26' newline 'H'. Scan number+letter pairs."""
    out = {}
    for i, l in enumerate(ans_lines[:-1]):
        if re.fullmatch(r"\d{2}", l):
            nxt = ans_lines[i + 1]
            if re.fullmatch(r"[A-R]", nxt):
                n = int(l)
                if 26 <= n <= 55 and n not in out:
                    out[n] = nxt
    return out


def extract_word_bank(sec_a: list[str]) -> dict[str, str]:
    """Bank: 'Word Bank: A) x B) y ...' inline, or one 'A) word' line per entry."""
    text = "\n".join(sec_a)
    bank = {}
    m = re.search(r"Word Bank:?([\s\S]*?)(?:📌|$)", text)
    if m:
        for mm in re.finditer(r"\b([A-O])\)\s*([a-zA-Z][a-zA-Z\-']*)", m.group(1)):
            bank[mm.group(1)] = mm.group(2).lower()
        return bank
    # fallback: one entry per line, e.g. 'A) anywhere'
    for l in sec_a:
        mm = re.fullmatch(r"([A-O])\)\s+([a-zA-Z][a-zA-Z\-']*)\s*", l)
        if mm:
            bank[mm.group(1)] = mm.group(2).lower()
    return bank


def parse_section_c_questions(sec_c: list[str]) -> list[dict]:
    """Questions 46-55: '46.' stem ... A) opt / B) opt ..."""
    text = "\n".join(sec_c)
    qs = []
    # split by question start markers
    marks = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?m)^(\d{2})\.\s", text)]
    for idx, (pos, num) in enumerate(marks):
        if not (46 <= num <= 55):
            continue
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(text)
        block = text[pos:end]
        m = re.match(r"\d{2}\.\s*(.*)", block, re.S)
        body = m.group(1)
        # find option markers
        # NOTE: use [ \t]* not \s* — \s would eat the newline and capture the next line
        opt_marks = [(mm.start(), mm.group(1), mm.group(2)) for mm in
                     re.finditer(r"(?m)^([A-D])\)[ \t]*(.*)$", body)]
        if len(opt_marks) < 4:
            continue
        stem = body[: opt_marks[0][0]].strip().replace("\n", " ")
        opts = {}
        for j, (opos, letter, first) in enumerate(opt_marks):
            oend = opt_marks[j + 1][0] if j + 1 < len(opt_marks) else len(body)
            chunk = body[opos:oend]
            # drop the leading 'A)' line remainder handling: use first + following lines
            lines_after = chunk.split("\n")
            parts = []
            if first.strip():
                parts.append(first.strip())
            for extra in lines_after[1:]:
                e = extra.strip()
                if not e:
                    continue
                if re.match(r"^[A-D]\)", e):
                    break
                parts.append(e)
            opts[letter] = " ".join(parts)
        if len(opts) == 4:
            qs.append({"num": num, "stem": stem, "options": opts})
    return qs


def parse_section_b(sec_b: list[str]) -> dict:
    text = "\n".join(sec_b)
    stmts = []
    # statements may be '36. text' or '1. 36. text' (dual numbering in some sets)
    marks = [(m.start(), int(m.group(2) or m.group(1)))
             for m in re.finditer(r"(?m)^(\d{1,2})\.\s*(?:(\d{2})\.\s)?", text)]
    for idx, (pos, num) in enumerate(marks):
        if not (36 <= num <= 45):
            continue
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(text)
        block = text[pos:end]
        stmt = re.sub(r"(?s)^\d{2}\.\s*", "", block)
        stmt = " ".join(l.strip() for l in stmt.split("\n") if l.strip())
        stmts.append({"num": num, "statement": stmt})
    para_count = None
    m = re.search(r"\(?([A-P])[-\s]?([A-P])\)?\s*paragraphs", text)
    if m:
        para_count = ord(m.group(2)) - ord(m.group(1)) + 1
    return {"statements": stmts, "paragraph_count": para_count}


# Manual bank overrides for OCR-degraded sets (recovered by inspection / cross-validated with xdf)
BANK_OVERRIDES = {
    "cet6_2025_06_1": {
        "A": "aesthetic", "B": "chronic", "C": "contaminated", "D": "conventionally",
        "E": "emissions", "F": "environment", "G": "hampering", "H": "incidentally",
        "I": "infringement", "J": "intrigued", "K": "juvenile", "L": "outlet",
        "M": "rotating", "N": "vibrations", "O": "weeding",
    },
    "cet6_2025_06_2": {
        "A": "bolsters", "B": "consequences", "C": "credentials", "D": "dramatically",
        "E": "enact", "F": "equity", "G": "especially", "H": "evasively",
        "I": "formidable", "J": "impetus", "K": "lavish", "L": "prioritize",
        "M": "suffices", "N": "sustained", "O": "tenured",
    },
    "cet6_2025_06_3": {
        "A": "adaptations", "B": "blasted", "C": "catastrophic", "D": "evolved",
        "E": "feat", "F": "interior", "G": "probing", "H": "recurrence",
        "I": "rigors", "J": "seemingly", "K": "survive", "L": "tempt",
        "M": "thrill", "N": "unanimously", "O": "unfolding",
    },
}


def parse_set(set_id: str, paper_file: str, ans_file: str) -> dict:
    paper = clean((SRC / paper_file).read_text(encoding="utf-8"))
    ans = clean((SRC / ans_file).read_text(encoding="utf-8"))
    rp = reading_part(paper)
    answers = extract_answers(ans)

    # locate section boundaries inside reading part
    idx_a = next((i for i, l in enumerate(rp) if re.match(r"Section A\b", l)), None)
    idx_b = next((i for i, l in enumerate(rp) if re.match(r"Section B\b", l)), None)
    idx_c = next((i for i, l in enumerate(rp) if re.match(r"Section C\b", l)), None)
    if None in (idx_a, idx_b, idx_c):
        raise ValueError(f"{set_id}: section markers not found A={idx_a} B={idx_b} C={idx_c}")

    sec_a = rp[idx_a:idx_b]
    sec_b = rp[idx_b:idx_c]
    sec_c = rp[idx_c:]

    bank = BANK_OVERRIDES.get(set_id) or extract_word_bank(sec_a)
    qs_c = parse_section_c_questions(sec_c)
    sec_b_data = parse_section_b(sec_b)

    return {
        "set": set_id,
        "answers": {str(k): v for k, v in sorted(answers.items())},
        "section_a": {"bank": bank},
        "section_b": sec_b_data,
        "section_c": qs_c,
    }


def main():
    out_dir = SRC / "parsed"
    out_dir.mkdir(exist_ok=True)
    for set_id, (p, a) in SETS.items():
        try:
            data = parse_set(set_id, p, a)
        except Exception as e:
            print(f"[FAIL] {set_id}: {e}")
            continue
        path = out_dir / f"{set_id}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        n_a = sum(1 for k in data["answers"] if 26 <= int(k) <= 35)
        n_b = sum(1 for k in data["answers"] if 36 <= int(k) <= 45)
        n_c = sum(1 for k in data["answers"] if 46 <= int(k) <= 55)
        print(f"[OK] {set_id}: answers A={n_a}/10 B={n_b}/10 C={n_c}/10, "
              f"bank={len(data['section_a']['bank'])}, secC questions={len(data['section_c'])}")


if __name__ == "__main__":
    main()
