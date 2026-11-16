# 六级真题 Section C（仔细阅读）逆向分析报告

> 以正确答案为锚点的逆向分析。样本：2024.12—2026.06 共 **12 套真题 × 10 题 = 120 题**（24 篇文章）。
> 逐题明细见 `secC_detail.csv`，逐题"来源句 vs 正确选项"素材见 `secC_pairs_dump.txt`，汇总数字见 `secC_summary.json`。分析脚本 `scripts/reverse_secC.py` 可重跑。

## 方法说明

- 从每套 raw.txt 抽取 Passage One / Passage Two 正文（自动剥离页眉页码与 OCR 噪音），按句子切分（每篇 **平均 21.9 句**，最少 12 句、最多 26 句）。
- 对每题：正确选项与每个句子计算**实词重合率**（去停用词 + 简单词干化后，选项实词被该句覆盖的比例），取最高者为"来源句"；并列时用题干重合率次级定位。
- **定位成功率：101/120（84.2%）**。其余 19 题正确选项与全文任何句子零词面重合（纯同义改写），词面法无法定位，位置统计只基于这 101 题（各处均标注 n）。
- 抽样核验：人工比对 8 个低覆盖率案例，7 个定位正确；1 个因干扰词撞车选错句。整体定位精度估计 >90%，位置统计存在少量噪声。
- 段落级统计不可得：原始 PDF 文本层不保留段落空行，无法可靠重建段落边界，故只用**句级位置**（来源句序号 / 总句数 × 100%）。

## 一、答案来源句在文章中的位置（n=101）

| 统计 | 值 |
|---|---|
| 均值 | 50.6% |
| 中位数 | 48.0% |
| 四分位 | Q1=20.0%，Q3=81.0% |

| 位置区间 | 题数 | 占比 |
|---|---|---|
| 0–20% | 25 | 24.8% |
| 20–40% | 13 | 12.9% |
| 40–60% | 21 | 20.8% |
| 60–80% | 16 | 15.8% |
| 80–100% | 26 | 25.7% |

按三分段：**前 1/3 有 37 题（36.6%），中 1/3 有 29 题（28.7%），后 1/3 有 35 题（34.7%）**。

**结论：答案来源句在全文近似均匀分布，两头（开头 20% 和结尾 20%）略密（各约 25%），但没有"答案集中在某一段"的规律可赌。**

## 二、题文同序性：非常强

按题目在文章内的次序（第 1 题 = 46/51 题，第 5 题 = 50/55 题）统计来源句位置：

| 题位 | n | 位置均值 | 位置中位数 |
|---|---|---|---|
| 第 1 题 | 17 | 18.4% | **9.5%** |
| 第 2 题 | 18 | 35.4% | 31.9% |
| 第 3 题 | 22 | 53.3% | 53.3% |
| 第 4 题 | 22 | 64.9% | 69.4% |
| 第 5 题 | 22 | 70.8% | **89.1%** |

相邻两题位置递增的情况：**平均每篇 3.0 / 4 对递增**；整篇 5 题严格递增的 **7/24 篇（29%）**；Kendall τ 均值 **0.604**（τ≥0.6 的有 14/24 篇，τ<0 仅 2 篇）。

**结论：虽然不是每篇都严格递增（29%），但"第 n 题对应全文 (n-1)/5 ～ n/5 区段"的趋势非常稳定。这是考场上最重要的定位先验。**

## 三、答案字母（ABCD）与来源句位置

正确选项字母分布（n=120）：**A 28、B 33、C 30、D 29** —— 高度均匀。

字母 × 位置交叉（n=101）：

| | A | B | C | D | 合计 |
|---|---|---|---|---|---|
| 前 1/3 | 11 | 8 | 13 | 5 | 37 |
| 中 1/3 | 5 | 8 | 7 | 9 | 29 |
| 后 1/3 | 7 | 11 | 9 | 8 | 35 |

**结论：看不到字母与位置的可靠关联（各格 n=5–13，差异在噪声范围内）。蒙题时字母分布均匀，无偏好可利用。**

## 四、选项改写强度：正确项是"深度改写"，不是"原文抄写"

实词覆盖率/新词率（n=120，词干化后统计）：

| 指标 | 均值 | 含义 |
|---|---|---|
| 正确选项对**来源句**的实词覆盖率 | **37.8%** | 正确项约 1/3 实词能在来源句找到原词 |
| 干扰项对**同一来源句**的覆盖率（均值/最大） | 15.4% / 27.2% | 干扰项在该句的词面痕迹远低于正确项 |
| 正确项对来源句的**新词率** | **62.2%** | 正确项 ~6 成实词是对来源句的同义替换 |
| 正确项对**全文**的新词率 | **52.9%** | 一半以上实词连全文都找不到原词 |
| 干扰项对**全文**的最大单句覆盖率 | **44.6%** | 干扰项常与"别的句子"词面高度重合 |
| 正确项 − 干扰项（对同一来源句）覆盖差 | +22.3 个百分点 | 120 题中 92 题正确项覆盖更高 |

三个关键洞察：

1. **正确选项 ≈ 来源句的同义改写**：平均只有 37.8% 的实词来自来源句原词，62.2% 是新词；甚至 52.9% 的实词在全文任何地方都找不到原词。**"找和原文一样的词"这个直觉恰恰是错的。**
2. **干扰项是"张冠李戴"型的多**：干扰项与全文某句的最大词面重合（44.6%）甚至高于正确项对来源句的重合（37.8%）——干扰项喜欢从**别的段落**搬运原词。所以词面重合度最高的选项反而是最危险的。
3. **但正确项在"它自己的来源句"上区分度明显**：对同一句，正确项覆盖 37.8% vs 干扰项 15.4%，差 22.3 个百分点。先定位"这句话在回答哪道题"，再看哪个选项改写了这句话，是可靠路径。

## 五、同义替换模式（人工抽样 20 对）

从 120 题的"来源句 → 正确选项"中人工抽样，典型替换对：

| # | 来源句用词 | 正确选项用词 | 出处 |
|---|---|---|---|
| 1 | determines what is considered beautiful | is **defined** by | 2024.12-1 Q51D |
| 2 | deplorable | **detrimental** | 2024.12-2 Q48D |
| 3 | a strong sense of **mastery** | a strong sense of **being in control** | 2024.12-1 Q50D |
| 4 | do little to **harm** children's learning | have little **impact** on children's learning | 2025.06-1 Q47A |
| 5 | the **struggle** goes against the pressure / **unrealistic** | a **fight** to remove pressure / **absurd** | 2024.12-1 Q52C |
| 6 | has become the new beauty ideal | is **now regarded as** the new beauty ideal | 2024.12-1 Q53A |
| 7 | **give up** their own interests | **sacrifice** of personal interests | 2025.12-2 Q48C |
| 8 | **inadequately resourced** schools | **poorly financed** schools | 2026.06-1 Q50A |
| 9 | is **frightening** to parents | **scares** parents | 2026.06-2 Q54B |
| 10 | is a **primary cause** of low achievement | is **mainly attributed** to school absences | 2025.06-1 Q46C |
| 11 | learn how to **handle** negative emotion / truly **afraid** | how to **tackle** it / **fear** | 2024.12-1 Q49C |
| 12 | closely **correlated** to time spent on social media | the **more** time..., the **more likely** they suffer | 2026.06-1 Q47B |
| 13 | information about how to **avoid becoming prey** | how to **avoid falling prey** to an attacker | 2024.12-1 Q48A |
| 14 | a **key factor** in bringing about order | **essential** to order | 2025.12-2 Q50C |
| 15 | **conceived** as a way of enabling humans to determine | **designed** to test | 2025.12-3 Q52C |
| 16 | a force that **feeds** itself | a force **fueling** itself | 2026.06-2 Q48B |
| 17 | a **significant proportion** of / **uses** humans as means | a **large part** of / **making use of** humans | 2025.12-3 Q54A |
| 18 | **rarely questioned** | **hardly ever disputed** | 2024.12-2 Q51A |
| 19 | a hunger for **respect and esteem** / acquisition of **material goods** | **fame and fortune** | 2025.06-3 Q49A |
| 20 | different people experience different levels of happiness | happiness **means different things** to different people | 2025.06-2 Q52C |

替换类型归纳：

- **同义词/近义词**（最常见）：deplorable→detrimental、frightening→scares、mastery→control、resourced→financed、questioned→disputed、handle→tackle、give up→sacrifice
- **句式重组**：主动↔被动（X determines what is beautiful ↔ it is defined by X）、因果倒装（X causes low achievement ↔ low achievement is attributed to X）、陈述↔比较级（correlated ↔ the more…the more）
- **具体→概括**：a hunger for respect and esteem + material goods → fame and fortune；different levels of happiness → means different things
- **极端改写（零词面重合）**：high arousal → extreme excitement（2024.12-1 Q46B）。此类 19/120 题（15.8%），选项与全文无任何共同实词。

## 六、对考生逆向复习的可操作含义

1. **定位先验（最有用）**：第 n 题直接去全文 (n-1)/5～n/5 的区段找——第 1 题看文章开头（中位位置 9.5%，常考首段细节/主旨），第 5 题看结尾（中位 89.1%，常考末段态度/建议）。但**不要赌"答案只在某一段"**：全文前中后各有约 1/3 的答案。
2. **选项判别准则**：与某句词面重合特别高的选项要警惕——很可能是从文章其他部分搬词的张冠李戴项（干扰项全文最大重合 44.6% > 正确项对来源句 37.8%）。正确做法：先确认"本题定位句"，再选"深度改写了这句话"的选项。
3. **改写是常态**：正确选项约 62% 的实词与来源句不同词、53% 连全文都找不到原词。平时精读每篇真题时，把"来源句 → 正确选项"的替换对（见第五节样式）整理成个人替换库，比背单词表更贴近考试。
4. **蒙题策略**：ABCD 分布均匀（28/33/30/29），与答案位置无关联，蒙题无字母偏好可用；同序规律（τ=0.604）意味着如果第 3 题定位到了文章 90% 处，多半是定位错了，回 (2/5, 3/5) 区段重找。
5. **零重合题的心理准备**：约 16% 的题选项与原文完全不同词（如 high arousal→extreme excitement）。这类题只能靠理解而非词面匹配，精读时要练习"这句话换个说法是什么"。

## 附：方法局限

- 来源句定位基于词干化后的词面重合，对 19 题（15.8%）零重合题无法定位（已剔除，各统计标注 n）；另有极少数题可能因干扰词撞车定位偏差（抽验误差率约 1/8）。
- 2025.06 三套为 OCR 文本，存在字符级噪音（如 instruiction、perpetuiate），会轻微压低覆盖率统计。
- 段落级位置不可得（PDF 文本层无段落空行）；句子总数受 OCR 断句影响有 ±1–2 句误差，对位置百分比影响很小。
- Kendall τ 为小样本（每篇 5 点）符号统计，未做显著性检验；样本 24 篇，结论以趋势解读为准。
