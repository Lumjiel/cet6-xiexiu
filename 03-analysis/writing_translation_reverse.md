# 六级写作（Part I）与翻译（Part IV）逆向分析报告

> 数据来源：9 套"学姐制作"解析（2024.12 / 2025.12 / 2026.06 各 3 套）的 9 篇参考范文与 9 篇参考译文；翻译中文原文 12 段（另含 2025.06 真题 OCR 版 3 段，该期解析为扫描件未 OCR、无范文，不纳入写作分析）。
> 生成脚本：`scripts/reverse_writing.py`；结构化数据：`03-analysis/writing_templates.json`。
> 所有频次均为脚本实测，诚实标注 n；人工校对之处单独说明。

---

## 一、写作（Part I）逆向

### 1.1 九套题目与开头句（begins with the sentence）

| 套次 | 指定开头句（范文第 1 句即抄写该句，9/9） |
|---|---|
| 2024.12-1 | To increase the likelihood of success, one should set realistic goals and work persistently towards them. |
| 2024.12-2 | Nowadays, more and more students have realized the importance of self-discipline in their personal growth. |
| 2024.12-3 | College provides a great opportunity for students to explore various possibilities and find the right path for themselves. |
| 2025.12-1 | Living in an increasingly competitive world, college students should better prepare themselves to confront various challenges. |
| 2025.12-2 | While striving for the Chinese Dream, young people enjoy more opportunities to realize their self-worth. |
| 2025.12-3 | It is believed that teachers can exert a profound influence on their students' academic pursuit and personal development. |
| 2026.06-1 | Faced with growing globalization, students realize that a deep understanding of traditional Chinese culture helps cultivate cultural confidence. |
| 2026.06-2 | With the trend of urbanization, it is vitally important for city residents to develop a stronger love for nature. |
| 2026.06-3 | In an era of rapid social development, it is vitally important to enhance young people's sense of responsibility. |

**规律**：开头句全部是"话题 + 应该/需要做某事"的议论文命题（观点已给出，不需自己立论）。题目句本身可直接当第 1 句抄写——9/9 套范文都是这么做的。

### 1.2 体量体征

| 指标 | 数据（9 套实测） |
|---|---|
| 词数分布 | 140 / 143 / 150 / 153 / 172 / 173 / 176 / 179 / 179（中位数 172） |
| 分期趋势 | 2024.12 三套：172–179 词；2025.12：143–179；2026.06：140–153（命题更贴近 150 词下限） |
| 句数 | 7–11 句 |
| 段落 | PDF 抽取丢失空行，无法精确计数；从行文看为无明显空行的连排（阅卷实际按功能分段看待） |

**结论**：写到 **150–180 词、8 句左右**即与官方范文体量一致，超出 200 词上限没有收益。

### 1.3 段落功能结构（9 篇全部一致）

```
第1句   抄题目句（9/9）
第2句   解释/定义/承接题目句（9/9）——"This principle is..." / "X is the ability to..." / "Indeed, ..."
第3-6句 主体：For instance/For example 举例 + Moreover/However 递进或转折（8/9 有举例）
第7-9句 结尾：In conclusion / Therefore 总结 + 呼吁（In conclusion 5/9；Therefore 8/9）
```

### 1.4 连接词与话语标记频次（按出现篇数/总次数）

| 连接词 | 篇数 | 总次数 | 功能 |
|---|---|---|---|
| Therefore | 8/9 | 8 | 结尾呼吁 |
| Moreover | 7/9 | 7 | 主体递进 |
| For instance | 6/9 | 7 | 举例 |
| In conclusion | 5/9 | 5 | 结尾 |
| Personally | 4/9 | 4 | 个人举例 |
| However | 3/9 | 3 | 转折 |
| For example | 2/9 | 2 | 举例（与 For instance 互补） |
| Indeed | 2/9 | 2 | 开头承接 |
| Additionally | 2/9 | 2 | 递进 |
| Not only…but also | 3/9 | 8 次 | 主体"并列表述" |
| I have found that | 3/9 | 3 | 个人经历 |
| which 定语从句 | 4/9 | — | 句子延展 |

### 1.5 高级替换词频（可背的"提分词"）

resilience(5)、essential(4)、persistence/persistent(6)、well-being(3)、crucial(3)、foster(3)、cultivate(2)、enhance(2)、navigate(2)、empower(2)、setbacks(2)、vital(2)、mindset(1)、synergy(1)、hands-on(1)、profound(1)。

### 1.6 句式骨架清单（按功能分组，标注来源）

骨架由脚本对 9 篇范文做"实词挖空"提取，人工整理为以下可复用框架：

**开头引入（第 1–2 句）**
1. `［抄题目句］` — 9/9
2. `This principle is fundamental in both academic and professional pursuits.` — 2024.12-1（适用于"某种做法重要"类题目）
3. `Indeed, ...` 承接句（把题目关键词换种说法再说一遍）— 2025.12-3、2026.06-1
4. `In today's (job market / China), ... has opened up numerous paths for ...` — 2025.12-1、2025.12-2
5. `X is the ability to ____ in the pursuit of ____.`（定义句）— 2024.12-2

**举例论证（主体）**
6. `For instance, a student who ____ is more likely to ____ than one who ____.` — 2024.12-1/2/3（对比式举例，"a student who" 3/9 篇出现）
7. `Personally, I have found that ____ not only ____ but also ____.` — 2025.12-1、2026.06-2/3（个人经历式举例）
8. `____, such as ____ and ____, which provide(s) ____ and ____.` — 2024.12-2、2025.12-1
9. `not only ____ but also ____`（全篇通用并列表述，8 次/9 篇中 3 篇）

**递进转折（主体）**
10. `Moreover, ____` — 7/9 篇
11. `However, ____` — 3/9 篇（如 "However, a goal, no matter how realistic, is merely a dream without persistent effort."）
12. `____ enables us to adapt to ____.` / `helping sb do`（现在分词收尾）— 2025.12-1、2026.06-3 等

**结尾呼吁（最后 2 句）**
13. `In conclusion, ____ is not merely ____ but ____ that empowers ____ to ____.` — 2024.12-2、2024.12-3
14. `Therefore, I believe that ____ should be a priority for ____.` — 2026.06-2/3（"should be a priority" 3/9）
15. `____ is essential for ____ to ____.` — 2025.12-1、2026.06-1/2（is essential 3 篇、is crucial 2 篇）
16. `Whether in study, career, or personal life, we should cultivate both ____ and ____.` — 2024.12-1

### 1.7 万能骨架（开头 2 句 + 主体 4–6 句 + 结尾 2 句，填空即成文）

```
[1] ［题目指定句，原样抄写］.
[2] Indeed, ［把题目句换个说法，如: this principle / this awareness ］
    plays a ［crucial / fundamental］ role in ［主题领域］.        ← 来源：2024.12-1、2025.12-3、2026.06-1

[3] ［主题领域］ is the ability to ［具体行为1］, ［具体行为2］,
    and ［具体行为3］.                                            ← 来源：2024.12-2（定义式展开）
[4] For instance, a ［student/person/young graduate］ who ［正面做法］
    is more likely to ［好结果］ than one who ［反面做法］.         ← 来源：2024.12-1/2/3
[5] Moreover, ［第二个好处/角度］, such as ［例1］ and ［例2］,
    which provide ［收益1］ and ［收益2］.                         ← 来源：7/9 篇有 Moreover；2024.12-2、2025.12-1
[6] However, without ［反面条件］, ［主题词］ is merely ［降级说法］.  ← 来源：2024.12-1（可选，凑字数+转折分）
[7] Personally, I have found that ［个人小经历］ not only ［收益1］
    but also ［收益2］.                                           ← 来源：2025.12-1、2026.06-2/3

[8] In conclusion, ［主题词］ is not merely a skill but a lifelong habit
    that empowers ［人群］ to ［远期目标］.                         ← 来源：2024.12-2、2024.12-3
[9] Therefore, I believe that ［题目关键词动词化］ should be a priority
    for every ［student/resident/young person］.                  ← 来源：2026.06-2/3、2024.12-2
```

填充顺序建议：第 4 句放"最具体、最好写"的例子；第 5 句的两个 such as 例可以只写名词短语（不用成句）；第 7 句个人经历可编（"I have found that setting daily goals..." 这类万能经历 2025.12-1 原文可整体借用）。8 句 ×20 词 ≈ 160 词，正好落在 150–180 区间。

---

## 二、翻译（Part IV）逆向

### 2.1 十二段话题分布（人工通读校对；关键词得分见 JSON）

| 套次 | 段落主题 | 类别 | 中文长度 |
|---|---|---|---|
| 2024.12-1 | 北斗卫星导航系统 | 科技 | 170 字 |
| 2024.12-2 | 洋山港自动化 | 科技/工程 | 173 字 |
| 2024.12-3 | 神舟载人航天 | 科技 | 171 字 |
| 2025.06-1 | 天宫空间站 | 科技 | 181 字 |
| 2025.06-2 | 粤港澳大湾区 | 经济/区域发展 | 179 字 |
| 2025.06-3 | 南水北调工程 | 工程 | 175 字 |
| 2025.12-1 | 尊老美德 | 社会美德 | 177 字 |
| 2025.12-2 | 自强自立精神 | 社会精神+科技 | 176 字 |
| 2025.12-3 | 节俭美德 | 社会美德 | 169 字 |
| 2026.06-1 | 远程医疗+AI | 科技应用 | 173 字 |
| 2026.06-2 | 电商助农/直播带货 | 科技+经济 | 175 字 |
| 2026.06-3 | 无人机产业 | 科技产业 | 177 字 |

**话题预测**：
- **中国发展成就叙事 9/12（75%）**：科技 6（北斗/航天/空间站/远程医疗/电商/无人机）、工程 2（洋山港/南水北调）、经济 1（大湾区）。全部是"正面成就宣传体"。
- **中华传统美德/精神 3/12（25%）**：尊老、节俭、自强自立。
- 文化遗产/历史朝代类（老六级常考）近三期**零命中**——备考应把重心从"四大发明/传统节日"转移到"现代中国成就 + 社会美德"。
- 每段 169–181 汉字，对应译文 105–139 词、4–7 句，即**每句中文约 25–35 字、译成 20–30 词**。

### 2.2 高频中文表达模式（12 段统计，脚本实测）

| 模式 | 次数 | 典型例子 |
|---|---|---|
| 年代/时代表达（2003年、近年来、自古以来、到2035年） | 9/12 段 | "2003年，神舟五号飞船发射成功" |
| 数字+单位（公里/立方米/亿元/个/名） | 8/12 段 | "总长4350公里""110多立方米""180多个项目" |
| 被/受到广泛(应用/认可/喜爱) | 4/12 段 | "北斗系统已广泛应用于…" |
| 是…的(重要组成/区域)之一 | 3/12 段 | "是世界上规模最大的深水港之一" |
| 拥有/坐拥（设施描述） | 3/12 段 | "拥有完善的交通基础设施" |
| 专有名词自带英文括号注释 | 2 次（正则计数，实际通读 10/12 段有，OCR 括号变形导致漏计） | 北斗（Beidou）、直播带货 (live-streaming commerce) |
| 使/让…成为 | 2 次 | "使中国成为世界上少数几个…国家之一" |
| 越来越多 | 2 次 | "为越来越多的国家和地区" |
| 旨在/致力于/不懈 | 2 次 | "经过不懈努力" |
| 不仅…也/还 | 2 次 | "不仅将建成…还将打造成…" |
| 例如/如…等 | 2 次 | "涉及空间生命科学、太空医学等领域" |
| 随着…的深入/发展 | 1 次 | "随着改革开放的不断深入" |

### 2.3 参考译文句型统计（9 篇译文实测）

| 句型 | 合计命中 | 每篇 0–3 次 |
|---|---|---|
| 被动语态（be/was + 过去分词，含 has been widely applied） | 8 | 6/9 篇出现 |
| such as 列举 | 3 | 4/9 篇 |
| 现在分词结果状语 ", making/enabling..." | 3 | 3/9 篇 |
| widely applied/recognized 类副词+被动 | 3 | 3/9 篇 |
| one of the few/... | 2 | 2/9 篇 |
| 定语从句 that/which | 2 | 2/9 篇 |
| since + 时间（自…以来） | 2 | 2/9 篇 |
| It is ... that 强调句 | 0 | 未出现 |

**结论**：参考译文的"高级句型"其实很朴素——**被动 + such as + making 结果状语** 是三大主力；强调句、倒装一次都没用。追求及格分不需要炫技，把主动句写对、被动句用熟即可。

### 2.4 翻译"保命句型包"（7 个框架，覆盖 12 段绝大多数句型）

1. **"A 的成功研制/发展是 B 的一项重大成就"**
   → `The successful development of ____ is a major (technological) achievement (that) China has made since ____.`
   来源：2024.12-1 原句。
2. **"经过不懈努力，攻克…，最终实现…"**
   → `Through unremitting efforts, ____ overcame ____ and ultimately achieved ____.`
   来源：2024.12-1。
3. **"使中国成为世界上少数几个…的国家之一"**
   → `..., making China one of the few countries in the world to ____.`
   来源：2024.12-1（现在分词结果状语，12 段中"使…成为"出现 2 次）。
4. **"已广泛应用于…、…、…等诸多领域"**
   → `____ has been widely applied in many fields such as ____, ____, and ____.`
   来源：2024.12-1、2025.12-1（widely+被动 3 次）。
5. **"A 是…的重要组成部分/是最大…之一"**
   → `____ is an important part of ____ / one of the largest ____ in the world.`
   来源：2024.12-2、2025.06-2。
6. **"近年来，…蓬勃发展/快速延伸"**
   → `In recent years, ____ has developed rapidly / is booming. With ____, more and more ____ can ____.`
   来源：2026.06-2、2026.06-3。
7. **"这是中华民族的传统美德，深深植根于…"**
   → `____ is a traditional virtue of the Chinese nation, deeply rooted in ____.`
   来源：2025.12-1、2025.12-3、2025.12-2（美德类万能开头）。

**数字处理规则**：
- 阿拉伯数字照抄（真题译文保留 2003、2022 等原样）；"亿 = 100 million，十亿 = billion"：4350 公里 → 4,350 km；500 亿立方米 → 50 billion cubic meters；数千亿元 → hundreds of billions of yuan；400-450 公里 → 400–450 km。
- 数字+单位是 8/12 段必考点，宁可少写修饰语也要把数字句写完整。

**专名处理规则**：
- 括号里给了英文的**直接照抄**（12 段中 10 段都自带英文注释：Beidou、Yangshan Port、Tiangong Space Station、frugality、live-streaming commerce、drone、high-definition、rejuvenation、Guangdong–Hong Kong–Macao Greater Bay Area、the South-to-North Water Diversion Project）。
- 没给英文的用"拼音/意译 + 上位类别词"兜底：如"嫦娥探月工程" → the Chang'e lunar exploration program。
- 抽象美德词必备小词库：virtue（美德）、moral integrity（道德）、frugality（节俭）、respect for the elderly（尊老）、self-reliance（自强自立）、harmony（和谐）、well-being（福祉）。

---

## 三、考前 7 天背诵清单

| 天 | 背什么 | 怎么填充 |
|---|---|---|
| D1 | 万能骨架第 1–2、8–9 句（开头+结尾 4 句） | 用 2026.06-3（责任感）题目填一遍开头结尾 |
| D2 | 骨架第 4、5、7 句（举例三件套） | 用 2024.12-2（自律）填：For instance, a student who... / Moreover, ... such as ... |
| D3 | 高级词 20 个：resilience / essential / crucial / cultivate / foster / empower / well-being / setbacks / navigate / persistence… | 每个词造一个填进骨架第 5/8 句的短语 |
| D4 | 翻译保命句型包 7 条（§2.4） | 对照 2024.12-1 中文原文逐句套写，再对参考译文 |
| D5 | 数字规则（亿/十亿换算）+ 专名照抄规则 + 美德词库 | 拿 2025.06-3（南水北调）专练数字句 |
| D6 | 限时模写：2026.06 任一套写作 30 分钟 + 翻译 30 分钟 | 严格套骨架；写完自查：≥150 词？有 For instance？结尾有 Therefore？ |
| D7 | 限时模写：2025.12 任一套 + 复盘 D6 错误 | 重点检查:主谓一致、时态（成就叙事用现在完成时）、被动语态 |

**三条铁律（从 9 篇范文逆向得出）**：
1. 写作第 1 句必须原样抄题目指定句，第 2 句用 Indeed/This principle is fundamental 承接——这一步不丢分。
2. 主体段无论什么话题，都套"For instance, a student who..."或"Personally, I have found that..."，例子可以编个人经历。
3. 翻译先拆中文长句为"主语+谓语"短句，成就类用现在完成时/被动语态，结尾一句套 "making China one of the few countries to ..."。
