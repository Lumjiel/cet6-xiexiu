# -*- coding: utf-8 -*-
"""Analyze parsed CET-6 reading data to find answer patterns per section.

Output: 03-analysis/analysis_report.md
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "02-parsed" / "parsed"
OUT = ROOT / "03-analysis"
OUT.mkdir(exist_ok=True)

SETS = sorted(SRC.glob("*.json"))

PAPER_RAW = {
    "cet6_2024_12_1": "2024.12六级真题第1套_raw.txt",
    "cet6_2024_12_2": "2024.12六级真题第2套_raw.txt",
    "cet6_2024_12_3": "2024.12六级真题第3套_raw.txt",
    "cet6_2025_06_1": "2025.06六级真题第1套_raw.txt",
    "cet6_2025_06_2": "2025.06六级真题第2套_raw.txt",
    "cet6_2025_06_3": "2025.06六级真题第3套_raw.txt",
    "cet6_2025_12_1": "cet6_2025_12_1_raw.txt",
    "cet6_2025_12_2": "cet6_2025_12_2_raw.txt",
    "cet6_2025_12_3": "cet6_2025_12_3_raw.txt",
    "cet6_2026_06_1": "cet6_2026_06_1_raw.txt",
    "cet6_2026_06_2": "cet6_2026_06_2_raw.txt",
    "cet6_2026_06_3": "cet6_2026_06_3_raw.txt",
}

HEDGES = r"\b(may|might|could|can|possibly|perhaps|probably|tend|tends|some|sometimes|often|likely|usually|generally|partly)\b"
ABSOLUTES = r"\b(all|never|only|must|always|none|no one|every|entirely|completely|totally|wholly|solely|exclusively|unavoidably|inevitably|impossible)\b"
STOP = set("the a an of to in on for with and or is are was were be been being it its that this these those they them their he she his her as at by from not no but if we our us you your".split())


def content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zA-Z]{3,}", text.lower()) if w not in STOP}


def guess_pos(word: str) -> str:
    w = word.lower()
    if w.endswith("ly"):
        return "adv"
    for suf in ("tion", "sion", "ment", "ness", "ity", "ance", "ence", "ism", "age", "ure"):
        if w.endswith(suf):
            return "noun"
    for suf in ("ive", "ous", "ful", "less", "able", "ible", "ic", "al", "ant", "ent"):
        if w.endswith(suf):
            return "adj"
    return "other"


def load_all():
    data = [json.loads(f.read_text(encoding="utf-8")) for f in SETS]
    return data


def sec_c_analysis(data, md):
    md.write("\n## Section C 仔细阅读（60题，分值最高）\n\n")
    rows, feats = [], []
    all_opts = []  # (is_correct, text, set, num)
    for d in data:
        ans = d["answers"]
        for q in d["section_c"]:
            n = str(q["num"])
            if n not in ans:
                continue
            correct = ans[n]
            rows.append(correct)
            for letter, text in q["options"].items():
                all_opts.append((letter == correct, text, d["set"], q["num"]))
    dist = Counter(rows)
    n = len(rows)
    md.write("### 答案分布\n\n| 选项 | 次数 | 占比 |\n|--|--|--|\n")
    for k in "ABCD":
        md.write(f"| {k} | {dist.get(k,0)} | {dist.get(k,0)/n:.0%} |\n")
    # consecutive repeats
    rep3 = sum(1 for i in range(2, n) if rows[i] == rows[i-1] == rows[i-2])
    md.write(f"\n连续3题同答案出现次数: **{rep3}** / {n-2} 个窗口\n")

    cor, wrg = [], []
    for is_c, text, *_ in all_opts:
        (cor if is_c else wrg).append(text)
    def stats(texts, name):
        hedge = sum(1 for t in texts if re.search(HEDGES, t, re.I)) / len(texts)
        absol = sum(1 for t in texts if re.search(ABSOLUTES, t, re.I)) / len(texts)
        lens = [len(t.split()) for t in texts]
        avg = sum(lens)/len(lens)
        return hedge, absol, avg
    ch, ca, cl = stats(cor, "correct")
    wh, wa, wl = stats(wrg, "wrong")
    md.write("\n### 选项特征对比（正确 vs 错误）\n\n| 特征 | 正确选项 | 错误选项 |\n|--|--|--|\n")
    md.write(f"| 含委婉词(may/might/some等) | {ch:.0%} | {wh:.0%} |\n")
    md.write(f"| 含绝对词(all/never/only等) | {ca:.0%} | {wa:.0%} |\n")
    md.write(f"| 平均词数 | {cl:.1f} | {wl:.1f} |\n")

    # 原词重合率: option content words present in its passage
    # build passage text per set/section C
    rates_c, rates_w = [], []
    for d in data:
        raw = (ROOT / "02-parsed" / PAPER_RAW[d["set"]]).read_text(encoding="utf-8")
        lines = [l.strip() for l in raw.split("\n")]
        idx = next((i for i, l in enumerate(lines) if re.search(r"Part III.*Reading", l)), None)
        rp = lines[idx:]
        idx_c = next(i for i, l in enumerate(rp) if re.match(r"Section C\b", l))
        sec_c_text = "\n".join(rp[idx_c:])
        passages = re.split(r"Passage (?:One|Two|Three)", sec_c_text)[1:]
        # strip questions/options appended inside each passage chunk
        cleaned = []
        for p in passages:
            m = re.search(r"(?m)^\s*(4[6-9]|5[0-5])\.\s", p)
            cleaned.append(p[: m.start()] if m else p)
        passages = cleaned
        ans = d["answers"]
        qs = [q for q in d["section_c"] if str(q["num"]) in ans]
        for i, q in enumerate(qs):
            p = passages[min(i // 5, len(passages)-1)] if passages else ""
            pw = content_words(p)
            if not pw:
                continue
            for letter, text in q["options"].items():
                ow = content_words(text)
                if not ow:
                    continue
                rate = len(ow & pw) / len(ow)
                (rates_c if letter == ans[str(q["num"])] else rates_w).append(rate)
    if rates_c and rates_w:
        avgc = sum(rates_c)/len(rates_c)
        avgw = sum(rates_w)/len(rates_w)
        md.write(f"\n### 原词重合率（选项实词出现在原文中的比例）\n\n")
        md.write(f"- 正确选项平均: **{avgc:.0%}**（n={len(rates_c)}）\n")
        md.write(f"- 错误选项平均: **{avgw:.0%}**（n={len(rates_w)}）\n")
        hi_c = sum(1 for r in rates_c if r >= 0.8)/len(rates_c)
        hi_w = sum(1 for r in rates_w if r >= 0.8)/len(rates_w)
        md.write(f"- 重合率≥80%的占比: 正确 {hi_c:.0%} vs 错误 {hi_w:.0%}\n")

    # length rank of correct option within its question
    import statistics
    ranks = []
    for d in data:
        ans = d["answers"]
        for q in d["section_c"]:
            nq = str(q["num"])
            if nq not in ans or len(q["options"]) != 4:
                continue
            lens = {k: len(t.split()) for k, t in q["options"].items()}
            sorted_by_len = sorted(lens, key=lens.get)
            ranks.append(sorted_by_len.index(ans[nq]) + 1)  # 1=shortest 4=longest
    if ranks:
        md.write(f"\n### 正确选项的长度排名（1=本题最短, 4=最长, n={len(ranks)}）\n\n")
        cnt = Counter(ranks)
        for r in (1, 2, 3, 4):
            md.write(f"- 排名 {r}: {cnt.get(r,0)} 次 ({cnt.get(r,0)/len(ranks):.0%})\n")
        md.write(f"\n正确选项恰为最短或次短的比例: {(cnt.get(1,0)+cnt.get(2,0))/len(ranks):.0%}\n")
    return rows


def sec_b_analysis(data, md):
    md.write("\n## Section B 段落匹配（60题）\n\n")
    rows = []
    for d in data:
        for n in range(36, 46):
            v = d["answers"].get(str(n))
            if v:
                rows.append(v)
    dist = Counter(rows)
    ordered = sorted(dist.items(), key=lambda x: -x[1])
    n = len(rows)
    md.write(f"### 段落字母分布（n={n}）\n\n被选中的字母跨度: {min(rows, key=lambda c: ord(c))} – {max(rows, key=lambda c: ord(c))}\n\n")
    md.write("| 排名 | 段落 | 次数 | 占比 |\n|--|--|--|\n")
    for i, (k, v) in enumerate(ordered[:8], 1):
        md.write(f"| {i} | {k} | {v} | {v/n:.0%} |\n")
    letters = sorted(set(rows))
    md.write(f"\n覆盖的不同段落字母数: **{len(letters)}** ({' '.join(letters)})\n")
    rep = sum(1 for i in range(1, n) if rows[i] == rows[i-1])
    md.write(f"相邻两题选同一段落的次数: {rep}\n")

    # per-set stats: distinct paragraphs per set + order monotonicity
    md.write("\n### 每套卷内部规律\n\n")
    for d in data:
        row = [d["answers"].get(str(n), "") for n in range(36, 46)]
        row = [r for r in row if r]
        distinct = len(set(row))
        idxs = [ord(r) - ord("A") for r in row]
        asc = sum(1 for i in range(1, len(idxs)) if idxs[i] > idxs[i-1])
        pairs = len(idxs) - 1
        md.write(f"- {d['set']}: 10题用了 **{distinct}** 个不同段落; 相邻题段落递增 {asc}/{pairs}\n")


def sec_a_analysis(data, md):
    md.write("\n## Section A 选词填空（60题）\n\n")
    rows, pos_counter = [], Counter()
    chosen_pos = Counter()
    for d in data:
        bank = d["section_a"]["bank"]
        for n in range(26, 36):
            v = d["answers"].get(str(n))
            if not v:
                continue
            rows.append(v)
            w = bank.get(v)
            if w:
                chosen_pos[guess_pos(w)] += 1
    dist = Counter(rows)
    n = len(rows)
    md.write("### 答案(词库字母)分布\n\n")
    md.write("| 字母 | " + " | ".join(sorted(dist)) + " |\n|--|" + "--|" * len(dist) + "\n")
    md.write("| 次数 | " + " | ".join(str(dist[k]) for k in sorted(dist)) + " |\n")
    md.write("\n### 被选中的词性分布（按后缀猜测）\n\n| 词性 | 次数 | 占比 |\n|--|--|--|\n")
    for pos in ("noun", "adj", "adv", "other"):
        c = chosen_pos.get(pos, 0)
        md.write(f"| {pos} | {c} | {c/n:.0%} |\n")


def main():
    data = load_all()
    md_lines = ["# 六级阅读邪修规律分析报告", "",
                f"数据: {len(data)} 套真题（2024.12、2025.06、2025.12、2026.06 四个考次各3套），"
                f"每套阅读30题（A/B/C各10题），共{len(data)*30}题。", ""]
    class MD:
        def write(self, s):
            md_lines.append(s.rstrip("\n"))
    md = MD()
    c_rows = sec_c_analysis(data, md)
    sec_b_analysis(data, md)
    sec_a_analysis(data, md)
    (OUT / "analysis_report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("saved 03-analysis/analysis_report.md")
    print("\n".join(md_lines))


if __name__ == "__main__":
    main()
