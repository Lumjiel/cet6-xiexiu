# -*- coding: utf-8 -*-
"""
Section C（仔细阅读）逆向分析：以正确答案为锚点。
- 从 raw.txt 中抽取每套题 Passage One / Passage Two 正文
- 句子切分后，用正确选项与干扰项的实词重合率定位"来源句"
- 统计：来源句位置、正确/干扰项重合率、新词率、题文同序性、答案字母×位置、替换模式素材
输出：
  03-analysis/secC_detail.csv          逐题明细
  03-analysis/secC_pairs_dump.txt      人工抽样同义替换用的素材（选项 vs 来源句）
  03-analysis/secC_summary.json        汇总统计（供报告引用）
"""
import json
import re
import csv
import math
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PARSED = ROOT / "02-parsed" / "parsed"
RAWDIR = ROOT / "02-parsed"
OUTDIR = ROOT / "03-analysis"
OUTDIR.mkdir(exist_ok=True)

RAW_MAP = {
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

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this", "these", "those",
    "of", "to", "in", "on", "at", "by", "for", "with", "about", "as", "into", "from", "over",
    "under", "between", "among", "through", "during", "before", "after", "above", "below",
    "is", "am", "are", "was", "were", "be", "been", "being", "do", "does", "did", "doing",
    "have", "has", "had", "having", "will", "would", "shall", "should", "can", "could",
    "may", "might", "must", "not", "no", "nor", "so", "too", "very", "just", "also",
    "i", "me", "my", "we", "our", "us", "you", "your", "he", "him", "his", "she", "her",
    "it", "its", "they", "them", "their", "theirs", "what", "which", "who", "whom", "whose",
    "when", "where", "why", "how", "there", "here", "one", "ones", "such", "own", "same",
    "other", "others", "another", "each", "any", "all", "both", "few", "more", "most",
    "some", "many", "much", "only", "up", "down", "out", "off", "again", "further",
    "because", "while", "until", "against", "upon", "within", "without", "toward", "towards",
    "according", "regarding", "concerning", "whether", "rather", "even", "ever", "never",
    "always", "often", "still", "yet", "well", "way", "ways", "thing", "things", "something",
    "anything", "nothing", "everything", "someone", "anyone", "everyone", "people", "person",
    "lot", "lots", "let", "make", "made", "get", "got", "go", "goes", "gone", "going",
    "say", "said", "says", "come", "came", "take", "took", "taken", "see", "saw", "seen",
    "give", "gave", "given", "use", "used", "using", "know", "knew", "known",
}

# ---------------------------------------------------------------- 文本清洗

PAGE_HEADER_RE = [
    re.compile(r"20\d{2}\s*年\d*\s*月英语六级真题第\d*\s*套\s*第\d*\s*页[，,]?\s*共\s*\d+\s*页"),
    re.compile(r"20\d{2}\s*年\d*\s*月英语六级真题第\d*\s*套"),
    re.compile(r"\b\d{1,2}\s*[:：]\s*\d{1,2}\b"),   # OCR 页码残留 "6: 9"
]
CJK_RE = re.compile(r"[（(][^（）()]*游[^（）()]*[)）]")   # (游戏化的) 之类注释
CJK_CHAR = re.compile(r"[\u4e00-\u9fff]+")

def clean_text(t: str) -> str:
    t = CJK_RE.sub(" ", t)
    for p in PAGE_HEADER_RE:
        t = p.sub(" ", t)
    t = CJK_CHAR.sub(" ", t)
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("——", ", ").replace("—", "-").replace("–", "-")
    t = re.sub(r"\bU\.\s*S\.", "U.S.", t)
    t = re.sub(r"\bU\.\s*K\.", "U.K.", t)
    t = re.sub(r"\s+", " ", t)
    # OCR 句子开头的孤立标点
    t = re.sub(r"(^|\s)[.:;,]\s+", r"\1", t)
    return t.strip()

MARKER_RE = re.compile(r"Passage\s+(One|Two)|Part\s*\.?\s*IV|Questions\s+\d+\s+to\s+\d+")

def clean_option(t: str) -> str:
    # 截掉粘连进来的后文（Passage Two 正文 / Part IV 等）
    m = MARKER_RE.search(t)
    if m:
        t = t[:m.start()]
    t = clean_text(t)
    t = re.sub(r"^\s*[A-D]\s*\)\s*", "", t)
    t = t.strip(" .,:;")
    # 兜底：仍超长的只保留第一句
    if len(t.split()) > 25:
        m = re.search(r"[.!?]", t)
        if m:
            t = t[: m.end()]
    return t

# ---------------------------------------------------------------- 结构抽取

def extract_passage_bodies(lines):
    """返回 [passage_one_lines, passage_two_lines]（正文行列表），以及诊断信息。"""
    text_lines = [l.rstrip("\n") for l in lines]
    # 找最后一个 Section C（阅读部分）
    sec_idx = [i for i, l in enumerate(text_lines) if re.match(r"^\s*Section C\b", l)]
    if not sec_idx:
        raise RuntimeError("no Section C")
    start = sec_idx[-1]
    end = len(text_lines)
    for i in range(start, len(text_lines)):
        if re.match(r"^\s*Part IV\b", text_lines[i]):
            end = i
            break
    region = text_lines[start:end]

    def find_marker(name):
        for i, l in enumerate(region):
            if re.match(r"^\s*" + name + r"\s*$", l.strip()) or l.strip().startswith(name):
                return i
        return None

    def find_question(num, after):
        pat = re.compile(r"^\s*\.?\s*%d\s*\.\s" % num)
        for i in range(after, len(region)):
            if pat.match(region[i]):
                return i
        return None

    p1 = find_marker("Passage One")
    p2 = find_marker("Passage Two")
    q46 = find_question(46, p1)
    q51 = find_question(51, p2 if p2 is not None else 0)
    if None in (p1, p2, q46, q51):
        raise RuntimeError(f"markers missing: p1={p1} p2={p2} q46={q46} q51={q51}")

    def body_lines(begin, stop):
        out = []
        for l in region[begin + 1: stop]:
            s = l.strip()
            if not s:
                out.append("")       # 保留空行作为段落边界
                continue
            if re.match(r"^Questions\s+\d+\s+to\s+\d+", s):
                continue
            out.append(s)
        return out

    return body_lines(p1, q46), body_lines(p2, q51)

# ---------------------------------------------------------------- 句子切分 / 段落

ABBREV_FIX = [
    (r"\be\s*\.\s*g\s*\.", "e.g."),
    (r"\bi\s*\.\s*e\s*\.", "i.e."),
]

def split_block_sentences(block_text: str):
    t = block_text.strip()
    if not t:
        return []
    for pat, rep in ABBREV_FIX:
        t = re.sub(pat, rep, t)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"(])", t)
    out = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p)
    # 合并过短碎片（OCR 断句噪音）
    merged = []
    for s in out:
        if merged and len(re.findall(r"[A-Za-z]{2,}", s)) < 3:
            merged[-1] = merged[-1] + " " + s
        elif len(re.findall(r"[A-Za-z]{2,}", s)) < 3 and not merged:
            continue
        else:
            merged.append(s)
    if merged and len(re.findall(r"[A-Za-z]{2,}", merged[0])) < 3 and len(merged) > 1:
        merged[1] = merged[0] + " " + merged[1]
        merged.pop(0)
    return merged

def build_sentences(body_lines):
    """body_lines: 行列表，'' 表示段落边界。返回 [(sent_text, para_idx, sent_in_para)]，及段落总数。"""
    blocks, cur = [], []
    for l in body_lines:
        if l == "":
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(l)
    if cur:
        blocks.append(cur)
    use_paras = len(blocks) >= 3
    if not use_paras:
        # 无法识别段落边界时，整篇视为一个块（para 信息置空）
        joined = [l for l in body_lines if l != ""]
        blocks = [joined] if joined else []
    sents = []
    for bi, blk in enumerate(blocks):
        # 处理行尾连字符换行
        text = ""
        for l in blk:
            l = l.rstrip()
            if text.endswith("-") and l and l[0].islower():
                text = text[:-1] + l
            else:
                text = text + " " + l if text else l
        ss = split_block_sentences(clean_text(text))
        for si, s in enumerate(ss):
            sents.append((s, bi if use_paras else None, si))
    return sents, (len(blocks) if use_paras else None)

# ---------------------------------------------------------------- 词干化 / 重合率

def stem(w: str) -> str:
    w = w.lower().strip("'")
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith(("sses", "shes", "ches", "xes", "zes")):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        w = w[:-1]
    if len(w) > 5 and w.endswith("ing"):
        w = w[:-3]
    elif len(w) > 5 and w.endswith("ed"):
        w = w[:-2]
    return w

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z'-]*")

def content_stems(text: str):
    """返回 {stem: 原词}（实词；去停用词、去数字）。"""
    out = {}
    for w in WORD_RE.findall(text):
        wl = w.lower().strip("'-")
        if wl in STOPWORDS or len(wl) < 3 or wl in ("u.s", "u.k"):
            continue
        st = stem(wl)
        if st in STOPWORDS or len(st) < 2:
            continue
        out.setdefault(st, wl)
    return out

def coverage(opt_stems: dict, sent_stems: dict) -> float:
    if not opt_stems:
        return 0.0
    hit = sum(1 for s in opt_stems if s in sent_stems)
    return hit / len(opt_stems)

# ---------------------------------------------------------------- 主流程

def kendall_tau(ys):
    n = len(ys)
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ys[i] < ys[j]:
                conc += 1
            elif ys[i] > ys[j]:
                disc += 1
    denom = n * (n - 1) / 2
    return (conc - disc) / denom if denom else None

def main():
    sets = sorted(RAW_MAP.keys())
    rows = []
    pair_dump = []
    order_stats = []          # 每篇 passage: (set, passage_no, [pct*5])
    letter_pos = Counter()    # (letter, bucket)
    letter_count = Counter()
    all_sents_total = []
    failed = []

    for sname in sets:
        data = json.load(open(PARSED / f"{sname}.json", encoding="utf-8"))
        answers = {int(k): v for k, v in data["answers"].items()}
        raw = open(RAWDIR / RAW_MAP[sname], encoding="utf-8").read().splitlines()
        b1, b2 = extract_passage_bodies(raw)

        for passage_no, (body, nums) in enumerate([(b1, range(46, 51)), (b2, range(51, 56))]):
            sents, para_total = build_sentences(body)
            sent_stems = [content_stems(s) for s, _, _ in sents]
            full_stems = {}
            for d in sent_stems:
                full_stems.update(d)
            all_sents_total.append((sname, passage_no, len(sents)))
            qs = [q for q in data["section_c"] if q["num"] in nums]
            qs.sort(key=lambda q: q["num"])
            pos_list = []

            for q in qs:
                num = q["num"]
                ans = answers.get(num)
                if ans is None or ans not in q["options"]:
                    failed.append((sname, num, "answer missing"))
                    continue
                corr = clean_option(q["options"][ans])
                wrongs = {k: clean_option(v) for k, v in q["options"].items() if k != ans}
                corr_stems = content_stems(corr)
                stem_q = content_stems(q.get("stem", ""))
                stem_covs = [coverage(stem_q, ss) for ss in sent_stems] if stem_q else [0.0] * len(sents)

                # 定位来源句：正确选项实词覆盖率最大；并列时用题干覆盖率次级定位
                covs = [coverage(corr_stems, ss) for ss in sent_stems]
                best = max(range(len(covs)), key=lambda i: (covs[i], stem_covs[i], -i))
                located = covs[best] > 0   # 纯同义改写（无词面重合）视为不可定位
                src_text, src_para, _ = sents[best]
                src_stems = sent_stems[best]
                pct = round(100.0 * best / max(1, len(sents) - 1), 1) if len(sents) > 1 else 0.0
                pos_list.append(pct)

                corr_cov = covs[best]
                corr_new = round(100.0 * (1 - corr_cov), 1)
                corr_new_full = round(100.0 * (1 - coverage(corr_stems, full_stems)), 1)
                # 干扰项：对来源句的覆盖率 + 对全文的最大覆盖率
                w_cov_src, w_max_full = [], []
                for wk, wt in wrongs.items():
                    ws = content_stems(wt)
                    w_cov_src.append(coverage(ws, src_stems))
                    w_max_full.append(max(coverage(ws, ss) for ss in sent_stems))
                wrong_avg_src = round(100.0 * sum(w_cov_src) / len(w_cov_src), 1)
                wrong_max_src = round(100.0 * max(w_cov_src), 1)
                wrong_avg_maxfull = round(100.0 * sum(w_max_full) / len(w_max_full), 1)
                wrong_new_src = round(100.0 - wrong_avg_src, 1)

                new_words = sorted({v for k, v in corr_stems.items() if k not in src_stems})
                old_words = sorted({v for k, v in corr_stems.items() if k in src_stems})

                rows.append({
                    "set": sname, "num": num, "answer_letter": ans,
                    "passage": passage_no + 1, "n_sents": len(sents),
                    "source_sent_idx": best, "source_sent_pct": pct,
                    "source_located": int(located),
                    "source_para_idx": (src_para + 1) if src_para is not None else "",
                    "para_total": para_total if para_total else "",
                    "correct_overlap_sent": round(100.0 * corr_cov, 1),
                    "wrong_avg_overlap_sent": wrong_avg_src,
                    "wrong_max_overlap_sent": wrong_max_src,
                    "wrong_avg_max_overlap_full": wrong_avg_maxfull,
                    "correct_new_word_pct": corr_new,
                    "wrong_avg_new_word_pct": wrong_new_src,
                    "correct_new_word_full_pct": corr_new_full,
                })
                letter_count[ans] += 1
                if located:
                    b = "前" if pct < 100 / 3 else ("中" if pct <= 200 / 3 else "后")
                    letter_pos[(ans, b)] += 1

                pair_dump.append(
                    f"### {sname} Q{num} 答案={ans} src={best}/{len(sents)} pct={pct} cov={corr_cov:.2f}\n"
                    f"[来源句] {src_text}\n[正确选项] {corr}\n"
                    f"[旧词] {' '.join(old_words) or '-'}\n[新词] {' '.join(new_words) or '-'}\n"
                )

            # 同序性（每篇 5 题）
            if len(pos_list) == 5:
                adj_inc = sum(1 for i in range(4) if pos_list[i + 1] > pos_list[i])
                order_stats.append({
                    "set": sname, "passage": passage_no + 1,
                    "positions": pos_list, "adjacent_increasing": adj_inc,
                    "kendall_tau": round(kendall_tau(pos_list), 3),
                    "strictly_increasing": adj_inc == 4,
                })

    # ---------------- 输出 CSV
    csv_path = OUTDIR / "secC_detail.csv"
    cols = ["set", "num", "answer_letter", "passage", "n_sents", "source_sent_idx",
            "source_sent_pct", "source_located", "source_para_idx", "para_total",
            "correct_overlap_sent", "wrong_avg_overlap_sent", "wrong_max_overlap_sent",
            "wrong_avg_max_overlap_full", "correct_new_word_pct",
            "wrong_avg_new_word_pct", "correct_new_word_full_pct"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    (OUTDIR / "secC_pairs_dump.txt").write_text("\n".join(pair_dump), encoding="utf-8")

    # ---------------- 汇总统计
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return round(sum(xs) / len(xs), 1) if xs else None

    def median(xs):
        xs = sorted(x for x in xs if x is not None)
        if not xs:
            return None
        n = len(xs)
        return round((xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2), 1)

    pcts = [r["source_sent_pct"] for r in rows]
    pcts_loc = [r["source_sent_pct"] for r in rows if r["source_located"]]
    buckets = Counter()
    for p in pcts_loc:
        lo = min(4, int(p // 20)) * 20
        buckets[f"{lo}-{lo + 20}"] += 1

    pos_vals = [r["source_sent_pct"] for r in order_stats if False]  # noqa
    flat_adj = [o["adjacent_increasing"] for o in order_stats]
    taus = [o["kendall_tau"] for o in order_stats]

    summary = {
        "n_questions": len(rows),
        "n_located": sum(r["source_located"] for r in rows),
        "n_failed": failed,
        "sent_counts_per_passage": [{"set": s, "passage": p + 1, "n": n} for s, p, n in all_sents_total],
        "source_pct": {
            "mean": mean(pcts_loc), "median": median(pcts_loc),
            "min": min(pcts_loc), "max": max(pcts_loc),
            "q1": sorted(pcts_loc)[len(pcts_loc) // 4], "q3": sorted(pcts_loc)[3 * len(pcts_loc) // 4],
            "buckets_20": dict(sorted(buckets.items())),
        },
        "coverage": {
            "correct_overlap_mean": mean([r["correct_overlap_sent"] for r in rows]),
            "wrong_avg_overlap_mean": mean([r["wrong_avg_overlap_sent"] for r in rows]),
            "wrong_max_overlap_mean": mean([r["wrong_max_overlap_sent"] for r in rows]),
            "wrong_maxfull_mean": mean([r["wrong_avg_max_overlap_full"] for r in rows]),
            "correct_new_word_mean": mean([r["correct_new_word_pct"] for r in rows]),
            "correct_new_word_full_mean": mean([r["correct_new_word_full_pct"] for r in rows]),
        },
        "order": {
            "n_passages": len(order_stats),
            "strictly_increasing": sum(o["strictly_increasing"] for o in order_stats),
            "adjacent_increasing_mean": mean(flat_adj),          # out of 4
            "adjacent_increasing_dist": dict(Counter(flat_adj)),
            "kendall_tau_mean": round(sum(taus) / len(taus), 3),
            "tau_dist": dict(Counter(taus)),
        },
        "letter_dist": dict(sorted(letter_count.items())),
        "letter_by_position": {"前(0-33%)": {}, "中(33-67%)": {}, "后(67-100%)": {}},
    }
    for (letter, b), c in letter_pos.items():
        key = {"前": "前(0-33%)", "中": "中(33-67%)", "后": "后(67-100%)"}[b]
        summary["letter_by_position"][key][letter] = c

    (OUTDIR / "secC_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTDIR / "secC_order.json").write_text(
        json.dumps(order_stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"完成：{len(rows)} 题，失败 {len(failed)}")
    for fail in failed[:10]:
        print("  FAIL:", fail)
    print("来源句位置 mean/median:", summary["source_pct"]["mean"], summary["source_pct"]["median"])
    print("正确项覆盖率 mean:", summary["coverage"]["correct_overlap_mean"],
          "新词率 mean:", summary["coverage"]["correct_new_word_mean"])
    print("同序：严格递增", summary["order"]["strictly_increasing"], "/", len(order_stats))

if __name__ == "__main__":
    main()
