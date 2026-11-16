# -*- coding: utf-8 -*-
"""逆向分析六级写作(Part I)与翻译(Part IV)：
从 9 套"学姐制作"解析中提取题目/范文/译文，统计句式骨架、连接词频、
翻译话题分布与中文表达模式，输出 JSON + 报告素材。
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
PARSED = ROOT / "02-parsed"
OUT_DIR = ROOT / "03-analysis"
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------- 数据定位
# 9 套解析（含题目回顾/写作思路/参考范文/参考译文）
ANS_FILES = {
    "2024.12-1": "nju_2024.12_解析第1套_raw.txt",
    "2024.12-2": "nju_2024.12_解析第2套_raw.txt",
    "2024.12-3": "nju_2024.12_解析第3套_raw.txt",
    "2025.12-1": "cet6_2025_12_1_ans_raw.txt",
    "2025.12-2": "cet6_2025_12_2_ans_raw.txt",
    "2025.12-3": "cet6_2025_12_3_ans_raw.txt",
    "2026.06-1": "cet6_2026_06_1_ans_raw.txt",
    "2026.06-2": "cet6_2026_06_2_ans_raw.txt",
    "2026.06-3": "cet6_2026_06_3_ans_raw.txt",
}
# 2025.06 解析为空（扫描件未 OCR），翻译中文段从真题 OCR 文本提取
CJ_EXTRA = {
    "2025.06-1": "2025.06六级真题第1套_raw.txt",
    "2025.06-2": "2025.06六级真题第2套_raw.txt",
    "2025.06-3": "2025.06六级真题第3套_raw.txt",
}


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def block_between(text: str, start: str, end_pat: str) -> str | None:
    """取 start 标记之后到下一个匹配 end_pat 的行之前的内容"""
    lines = text.splitlines()
    collecting = False
    buf = []
    for ln in lines:
        s = ln.strip()
        if not collecting:
            if s.startswith(start):
                collecting = True
            continue
        if re.search(end_pat, s):
            break
        buf.append(ln)
    return "\n".join(buf).strip() if collecting else None


def split_sentences(text: str) -> list[str]:
    joined = re.sub(r"\s+", " ", text)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if s.strip()]
    return sents


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z'’\-]+", text)


# ---------------------------------------------------------------- 写作提取
essays = {}
for sid, fn in ANS_FILES.items():
    t = read(PARSED / fn)
    prompt = block_between(t, "题目回顾：", r"写作思路：")
    model = block_between(t, "参考范文：", r"Part II")
    trans = block_between(t, "参考译文：", r"翻译要点|Part |全真试题")
    cn = block_between(t, "题目原文：", r"参考译文：")
    essays[sid] = {
        "prompt": prompt or "",
        "model_essay": model or "",
        "ref_translation": trans or "",
        "chinese_source": cn or "",
        "src_file": fn,
    }

# ---------------------------------------------------------------- 写作统计
essay_stats = {}
for sid, e in essays.items():
    sents = split_sentences(e["model_essay"])
    wc = len(words(e["model_essay"]))
    blocks = [b for b in re.split(r"\n\s*\n", e["model_essay"].strip()) if b.strip()]
    essay_stats[sid] = {
        "given_sentence": sents[0] if sents else "",
        "word_count": wc,
        "sentence_count": len(sents),
        "paragraph_blocks": len(blocks),  # PDF 抽取压平后多为 1 块
        "sentences": sents,
    }

# ---- 句式骨架挖掘：功能词保留，实词挖空 ----
FUNC_WORDS = {
    # 限定/冠词/介词
    "the","a","an","of","to","in","on","for","with","as","by","at","from","into","over",
    "under","about","between","among","through","during","without","within","upon","across",
    "toward","towards","behind","beyond","along","around","against","before","after",
    # be/助动词
    "is","are","was","were","be","been","being","am","has","have","had","do","does","did",
    "can","could","will","would","should","may","might","must","shall","not","no",
    # 代词
    "it","its","this","that","these","those","there","we","our","us","they","their","them",
    "you","your","i","my","me","he","she","his","her","one","ones","oneself","themselves",
    "ourselves","ours","yours","himself","herself","itself","who","whom","whose","which","what",
    # 连词
    "and","or","but","if","so","than","when","while","whether","because","since","although",
    "though","yet","unless","until","once","where","wherever",
    # 语篇功能词（模板核心，保留）
    "however","moreover","furthermore","additionally","therefore","thus","consequently",
    "hence","indeed","also","too","besides","meanwhile","instead","otherwise","finally",
    "first","firstly","second","secondly","third","thirdly","last","lastly","then","next",
    "still","even","ever","never","always","often","only","just","such","own","same","both",
    "each","all","any","some","much","many","more","most","less","least","few","very","quite",
    "in","conclusion","instance","example","take","taking","taken","notably","importantly",
    "increasingly","today","nowadays","now","here","personal","personally","believe","believed",
    "regarded","regard","considered","consider","denying","denied","deny","essential",
    "crucial","vital","important","significant","necessary","better","best","grow","growing",
    "grows","develop","developing","developed","development","play","plays","played","role",
    "roles","part","become","becomes","becoming","enable","enables","enabling","enabled",
    "make","makes","making","made","help","helps","helping","helped","bring","brings",
    "bringing","brought","lead","leads","leading","led","contribute","contributes",
    "contributing","contributed","contribution","provide","provides","providing","provided",
    "offer","offers","offering","offered","enhance","enhances","enhancing","enhanced",
    "improve","improves","improving","improved","gain","gains","gaining","gained","achieve",
    "achieves","achieving","achieved","build","builds","building","built","create","creates",
    "creating","created","become","cultivate","cultivates","cultivating","cultivated",
    "strengthen","strengthens","strengthening","strengthened","boost","boosts","boosting",
    "boosted","foster","fosters","fostering","fostered","possess","possesses","possessing",
    "possessed","embody","embodies","embodying","embodied","involves","involve","involving",
    "involved","include","includes","including","included","reduce","reduces","reducing",
    "reduced","remain","remains","remaining","remained","stay","stays","staying","stayed",
    "face","faces","facing","faced","confront","confronts","confronting","confronted",
    "meet","meets","meeting","met","exceed","exceeds","exceeding","exceeded","apply",
    "applies","applying","applied","turn","turns","turning","turned","give","gives","giving",
    "given","set","sets","setting","needs","need","needing","needed","start","starts",
    "starting","started","deepen","deepens","deepening","deepened","adapt","adapts",
    "adapting","adapted","engage","engages","engaging","engaged","require","requires",
    "requiring","required","allows","allow","allowing","allowed","seem","seems","seeming",
    "seemed","looks","look","looking","looked","finding","find","finds","found","know",
    "knows","knowing","known","realize","realizes","realizing","realized","realise",
    "realises","realising","realised","come","comes","coming","came","go","goes","going",
    "went","get","gets","getting","got","keep","keeps","keeping","kept","begin","begins",
    "beginning","began","end","ends","ending","ended","use","uses","using","used","new",
    "modern","young","great","good","strong","stronger","long","high","life","world",
    "time","way","ways","goal","goals","success","students","student","people","college",
    "chinese","culture","cultural","challenges","challenge","knowledge","skills","skill",
}
# 加以 -ly 结尾的副词与 to/in+动词 等通用结构由规则兜底


def normalize_w(w: str) -> str:
    return w.lower().strip("'’")


def skeleton_of(sent: str) -> str:
    toks = re.findall(r"[A-Za-z'’]+|[^\sA-Za-z'’]+", sent)
    out = []
    for tk in toks:
        if re.match(r"^[A-Za-z'’]+$", tk):
            w = normalize_w(tk)
            if re.search(r"ly$", w) and w not in FUNC_WORDS:
                out.append("____")  # 未收录副词视为可替换
            elif w in FUNC_WORDS:
                out.append(tk.lower())
            else:
                out.append("____")
        else:
            out.append(tk if re.match(r"^[,;:.!?]$", tk) else "____")
    # 合并连续挖空
    merged, pending = [], False
    for tk in out:
        if tk == "____":
            pending = True
        else:
            if pending:
                merged.append("____")
                pending = False
            merged.append(tk)
    if pending:
        merged.append("____")
    return " ".join(merged).strip()


def skeleton_group(sk: str, sent_idx: int, sent_total: int) -> str:
    sk_l = sk.lower()
    first_zone = sent_idx <= 1
    last_zone = sent_idx >= sent_total - 2
    if any(k in sk_l for k in ["instance", "example", "such as"]):
        return "举例"
    if any(k in sk_l for k in ["however", "moreover", "furthermore", "additionally",
                               "in addition", "not only", "instead"]):
        return "递进转折"
    if any(k in sk_l for k in ["therefore", "thus", "consequently", "because", "hence"]):
        return "因果"
    if any(k in sk_l for k in ["in conclusion", "to conclude", "in summary"]) or (
        last_zone and re.search(r"____ (should|must)", sk_l)
    ):
        return "结尾呼吁"
    if first_zone:
        return "开头引入"
    return "主体论证"


# ---- 采集全部句子 → 骨架频次（整句骨架 + 子序列 frame 挖掘）----
sk_counter = Counter()
sk_group = defaultdict(Counter)   # group -> skeleton -> count
frame_counter = Counter()         # 子序列 frame（3-8 词，含挖空）


def frames_from(tokens: list[str], min_n: int = 3, max_n: int = 8) -> list[tuple]:
    out = []
    for n in range(min_n, max_n + 1):
        for i in range(len(tokens) - n + 1):
            out.append(tuple(tokens[i:i + n]))
    return out


PUNCT = {",", ".", ";", ":", "!"}


def frame_ok(fr: tuple) -> bool:
    if "____" not in fr:
        return False
    anchors = [t for t in fr if t != "____" and t not in PUNCT]
    return len(anchors) >= 2


for sid, st in essay_stats.items():
    n = len(st["sentences"])
    for i, s in enumerate(st["sentences"]):
        sk = skeleton_of(s)
        if sk.count("____") < 1 or len(sk.split()) < 4:
            continue
        sk_counter[sk] += 1
        g = skeleton_group(sk, i, n)
        sk_group[g][sk] += 1
        for fr in frames_from(sk.split()):
            if frame_ok(fr):
                frame_counter[fr] += 1

# 去掉被更长同频 frame 包含的短 frame（保留信息量更大的版本）
frames_sorted = sorted(frame_counter.items(), key=lambda kv: (kv[1], len(kv[0])), reverse=True)
frames_final = []
for fr, n in frames_sorted:
    if n < 2:
        continue
    contained = False
    for fr2, n2 in frames_sorted:
        if n2 >= n and len(fr2) > len(fr) and fr2.count("____") >= fr.count("____"):
            # fr2 是否在任意位置包含 fr（连续子序列）
            for i in range(len(fr2) - len(fr) + 1):
                if tuple(fr2[i:i + len(fr)]) == fr:
                    contained = True
                    break
        if contained:
            break
    if not contained:
        frames_final.append((" ".join(fr), n))
frames_final.sort(key=lambda x: -x[1])

TEMPLATED_PHRASES = [
    # 开头
    r"there is no denying that", r"in today'?s", r"nowadays,?", r"with the (increasing|rapid|growing)",
    r"as (is )?known to all", r"it is widely (acknowledged|accepted|recognized)",
    r"living in", r"faced with", r"in an era where", r"this principle is",
    # 举例
    r"for instance", r"for example", r"take .{0,30} as an example", r"such as",
    r"a (student|person) who", r"personally,", r"i have found that",
    # 递进/转折
    r"in addition", r"additionally", r"moreover", r"furthermore", r"however", r"nevertheless",
    r"not only .{0,40} but also", r"on the one hand", r"meanwhile",
    # 因果
    r"therefore", r"thus", r"consequently", r"as a result", r"due to", r"thanks to",
    r"(enable|enables|enabling) .{0,20} to", r"lead(s)? to", r"contribute(s|d)? to",
    # 结尾
    r"in conclusion", r"to conclude", r"in summary", r"i believe that", r"it is (high )?time",
    r"should (cultivate|develop|keep|start|strive|remember)", r"only by", r"we should",
]
phrase_counter = Counter()
all_model_text = " ".join(" ".join(st["sentences"]) for st in essay_stats.values())
all_model_text = re.sub(r"\s+", " ", all_model_text)
for pat in TEMPLATED_PHRASES:
    n = len(re.findall(pat, all_model_text, flags=re.I))
    if n:
        phrase_counter[pat] = n

# ---- 连接词与高级替换词频 ----
CONNECTORS = ["Firstly", "Second", "Third", "Furthermore", "Moreover", "In addition",
              "Additionally", "Besides", "However", "Nevertheless", "Therefore", "Thus",
              "Consequently", "As a result", "In conclusion", "To conclude", "For instance",
              "For example", "Indeed", "Personally", "Meanwhile", "Not only", "Only by",
              "On the other hand", "In other words"]
ADV_WORDS = ["crucial", "essential", "vital", "significant", "fundamental", "indispensable",
             "cultivate", "foster", "enhance", "boost", "promote", "possess", "embody",
             "resilience", "synergy", "mindset", "navigate", "empower", "profound",
             "persistence", "persistent", "relentlessly", "unremitting", "well-being",
             "hands-on", "setbacks", "adaptability", "practical"]
conn_counter = Counter({c: len(re.findall(re.escape(c), all_model_text, re.I)) for c in CONNECTORS})
conn_counter = Counter({k: v for k, v in conn_counter.items() if v})
adv_counter = Counter({c: len(re.findall(re.escape(c), all_model_text, re.I)) for c in ADV_WORDS})
adv_counter = Counter({k: v for k, v in adv_counter.items() if v})

# ---------------------------------------------------------------- 翻译统计
# 12 段中文：9 段来自解析，3 段来自 2025.06 真题
for sid, fn in CJ_EXTRA.items():
    t = read(PARSED / fn)
    lines = t.splitlines()
    cj_lines, in_part4 = [], False
    after_directions = False
    empty_run = 0
    for ln in lines:
        s = ln.strip()
        if re.search(r"Part\s*\.?\s*IV", s):
            in_part4 = True
            continue
        if in_part4:
            if re.search(r"Directions", s, re.I):
                after_directions = True
                continue
            if after_directions:
                has_cn = bool(re.search(r"[\u4e00-\u9fff]", s))
                if has_cn and not re.search(r"答题卡|试题册|正式开考|违规|姓名|信息", s):
                    cj_lines.append(s)
                    empty_run = 0
                else:
                    empty_run += 1
                    if empty_run >= 3 and cj_lines:
                        break
    essays[sid] = {"chinese_source": "\n".join(cj_lines), "ref_translation": "",
                   "src_file": fn, "prompt": "", "model_essay": ""}

cn_passages = {sid: e["chinese_source"] for sid, e in essays.items() if e["chinese_source"]}

TOPIC_KW = {
    "科技": ["卫星", "导航", "系统", "技术", "智能", "网络", "数字", "航天", "空间站", "实验",
            "北斗", "人工智能", "机器人", "芯片", "通信", "互联网", "探测", "科学", "育种", "轨道"],
    "工程/基建": ["桥", "隧道", "铁路", "高铁", "港", "大坝", "建筑", "工程", "基建", "高速公路",
                "水利", "核电", "机场"],
    "文化": ["文化", "传统", "书法", "绘画", "戏曲", "节日", "春节", "民俗", "艺术", "文学",
            "茶", "瓷器", "京剧", "哲学", "文明", "遗址", "名胜", "工艺", "刺绣", "剪纸"],
    "历史": ["朝", "代", "历史", "考古", "遗产", "古代", "发明", "公元", "世纪", "文献"],
    "社会/经济": ["经济", "教育", "就业", "城市", "人口", "社区", "志愿", "健康", "医疗", "效益",
                "发展", "生活", "改革", "开放", "企业", "市场"],
    "地理/自然": ["长江", "黄河", "火山", "湖", "山", "自然保护区", "生态", "气候", "河流", "平原"],
}
topic_result = {}
topic_counter = Counter()
# 人工校对话题（基于通读原文；关键词得分保留作证据）
MANUAL_TOPICS = {
    "2024.12-1": "科技-北斗导航",
    "2024.12-2": "科技/工程-洋山港自动化",
    "2024.12-3": "科技-载人航天",
    "2025.06-1": "科技-天宫空间站",
    "2025.06-2": "经济-粤港澳大湾区",
    "2025.06-3": "工程-南水北调",
    "2025.12-1": "社会美德-尊老",
    "2025.12-2": "社会精神+科技-自强自立",
    "2025.12-3": "社会美德-节俭",
    "2026.06-1": "科技应用-远程医疗",
    "2026.06-2": "科技+经济-电商助农",
    "2026.06-3": "科技产业-无人机",
}
for sid, txt in cn_passages.items():
    scores = {}
    for topic, kws in TOPIC_KW.items():
        n = sum(txt.count(k) for k in kws)
        if n:
            scores[topic] = n
    best = max(scores, key=scores.get) if scores else "其他"
    topic_counter[MANUAL_TOPICS.get(sid, best)] += 1
    topic_result[sid] = {"topic_keyword": best, "topic_manual": MANUAL_TOPICS.get(sid, best),
                         "scores": scores,
                         "length_cn": len(re.findall(r"[\u4e00-\u9fff]", txt))}

# 中文表达模式
CN_PATTERNS = {
    "随着…的发展/进步": r"随着[^。]{0,25}的?(发展|进步|普及|提高|深入)",
    "是…的重要组成/之一": r"(是|已成为|成为)[^。]{0,35}之一",
    "被/受到广泛(应用|认可)": r"(被|受到|得到)[^。]{0,12}(广泛|普遍|越来越多)",
    "数字+单位": r"\d+[多几余]?(个|年|公里|千米|米|立方米|平方|座|项|种|条|亿元|万人|吨|摄氏度|小时|层|倍|部|名)",
    "朝代/年代": r"[唐宋元明清汉秦隋]|(20|19|18)世纪|\d{3,4}年",
    "专名+英文括号注释": r"[\u4e00-\u9fff]{2,12}（[A-Za-z][A-Za-z ]{1,30}）",
    "拥有/坐拥": r"(拥有|坐拥|占地面积)",
    "位于/距…公里": r"(位于|距[^。]{0,10}公里|地处)",
    "不仅…也/还": r"不仅[^。]{0,40}(也|还|而且)",
    "被誉为/标志着": r"(被誉为|标志着|象征)",
    "使/让…成为": r"(使|让|令)[^。]{0,30}成为",
    "越来越多": r"越来越多",
    "例如/如…等": r"(例如|如[^。]{0,15}等|诸如)",
    "旨在/致力于": r"(旨在|致力于|努力|不懈)",
}
cn_pat_counter = Counter()
for sid, txt in cn_passages.items():
    for name, pat in CN_PATTERNS.items():
        n = len(re.findall(pat, txt))
        if n:
            cn_pat_counter[name] += n

# 参考译文句型（9 套有译文）
trans_stats = {}
EN_PATTERNS = {
    "被动语态(be + 过去分词)": r"\b(?:is|are|was|were)\s+(?:\w+ly\s+)?\w+ed\b|\b(?:has|have|had)\s+been\s+(?:\w+ly\s+)?\w+(?:ed|en)\b",
    "定语从句(that/which/who)": r"\b(that|which|who)\b",
    "one of the …": r"\bone of (the|few)",
    "现在分词结果状语(making/enabling…)": r"\b(making|enabling|turning|allowing|reflecting)\b",
    "It is … that 强调/主语从句": r"\bIt (is|was) [^.]{0,50}\bthat\b",
    "with the development of": r"with the (development|growth|spread)",
    "widely (applied|used|recognized|known)": r"widely \w+ed",
    "since + 时间(自…以来)": r"\bsince\b",
    "such as / many fields such as": r"\bsuch as\b",
    "获得广泛认可(gained wide recognition)": r"gained (wide|international|increasing) \w+|growing (recognition|acceptance)",
}
for sid, e in essays.items():
    tr = e["ref_translation"]
    if not tr:
        continue
    sents = split_sentences(tr)
    stats = {"sentence_count": len(sents), "word_count": len(words(tr)), "hits": {}}
    for name, pat in EN_PATTERNS.items():
        n = len(re.findall(pat, tr, re.I))
        if n:
            stats["hits"][name] = n
    trans_stats[sid] = stats

# ---------------------------------------------------------------- 输出
result = {
    "essays": {sid: {k: essays[sid][k] for k in ("given_sentence",) if False} for sid in ()},
}
writing_out = {
    sid: {
        "given_sentence": essay_stats[sid]["given_sentence"],
        "word_count": essay_stats[sid]["word_count"],
        "sentence_count": essay_stats[sid]["sentence_count"],
        "model_essay": essays[sid]["model_essay"],
        "prompt": essays[sid]["prompt"],
    }
    for sid in essays if essays[sid]["model_essay"]
}
json_out = {
    "writing": {
        "essays": writing_out,
        "word_counts": {s: essay_stats[s]["word_count"] for s in writing_out},
        "skeletons_top": sk_counter.most_common(60),
        "skeletons_by_group": {g: c.most_common() for g, c in sk_group.items()},
        "frames_final": frames_final,
        "phrase_hits": phrase_counter.most_common(),
        "connector_freq": conn_counter.most_common(),
        "advanced_word_freq": adv_counter.most_common(),
    },
    "translation": {
        "passages": {sid: {"topic_keyword": topic_result[sid]["topic_keyword"] if sid in topic_result else "其他",
                           "topic_manual": topic_result[sid].get("topic_manual", "") if sid in topic_result else "",
                           "text": txt} for sid, txt in cn_passages.items()},
        "topic_distribution": dict(topic_counter),
        "chinese_pattern_freq": cn_pat_counter.most_common(),
        "translation_sentence_stats": trans_stats,
    },
}
(OUT_DIR / "writing_templates.json").write_text(
    json.dumps(json_out, ensure_ascii=False, indent=2), encoding="utf-8"
)

# 控制台摘要（供撰写报告用）
print("== 写作 9 套 ==")
for sid in writing_out:
    st = essay_stats[sid]
    print(f"{sid}: {st['word_count']}词 / {st['sentence_count']}句 / 段块{st['paragraph_blocks']}")
print("\n词数分布:", sorted(essay_stats[s]['word_count'] for s in writing_out))
print("\n== 骨架(整句,出现>=2次) ==")
for sk, n in sk_counter.most_common():
    if n >= 2:
        print(f"[{n}] {sk}")
print("\n== 高频 frame 挖空模板(>=2次) ==")
for s, n in frames_final[:60]:
    print(f"[{n}] {s}")
print("\n== frame 按功能分组(>=2) ==")
for g in ["开头引入", "举例", "递进转折", "因果", "结尾呼吁", "主体论证"]:
    items = [(s, n) for s, n in frames_final if n >= 2 and skeleton_group(s.replace("____", "____"), 99, 1 if g == "结尾呼吁" else 0) == g]
    # 直接用关键词重分组
    if g == "开头引入":
        items = [(s, n) for s, n in frames_final if re.search(r"there is no denying|in today|nowadays|with the|this principle|living in|faced with|in an era", s, re.I)]
    elif g == "举例":
        items = [(s, n) for s, n in frames_final if re.search(r"instance|example|such as|personally", s, re.I)]
    elif g == "递进转折":
        items = [(s, n) for s, n in frames_final if re.search(r"however|moreover|furthermore|additionally|in addition|not only|nevertheless", s, re.I)]
    elif g == "因果":
        items = [(s, n) for s, n in frames_final if re.search(r"therefore|thus|consequently|because|hence|enable|lead|contribute", s, re.I)]
    elif g == "结尾呼吁":
        items = [(s, n) for s, n in frames_final if re.search(r"in conclusion|to conclude|i believe|we should|it is (high )?time|only by|is essential|is crucial", s, re.I)]
    if items:
        print(f"-- {g} --")
        for s, n in items[:15]:
            print(f"  [{n}] {s}")
print("\n== 固定短语命中 ==")
for p, n in phrase_counter.most_common():
    print(f"[{n}] {p}")
print("\n== 连接词频 ==")
print(dict(conn_counter))
print("\n== 高级词频 ==")
print(dict(adv_counter))
print("\n== 翻译话题分布(关键词法) ==", dict(Counter(v["topic_keyword"] for v in topic_result.values())))
print("== 翻译话题分布(人工校对) ==", dict(topic_counter))
for sid, tr_ in topic_result.items():
    print(f"  {sid}: kw={tr_['topic_keyword']}  manual={tr_['topic_manual']}  ({tr_['length_cn']}汉字)  {tr_['scores']}")
print("\n== 中文表达模式 ==")
for p, n in cn_pat_counter.most_common():
    print(f"[{n}] {p}")
print("\n== 译文句型统计 ==")
agg = Counter()
for sid, st in trans_stats.items():
    print(f"  {sid}: {st['word_count']}词/{st['sentence_count']}句 {st['hits']}")
    for k, v in st["hits"].items():
        agg[k] += v
print("  合计:", dict(agg))
