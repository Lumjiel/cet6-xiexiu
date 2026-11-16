# cet6-xiexiu · 六级逆向分析项目

以正确答案为锚点，逆向分析六级真题的命题规律，产出可执行的复习方法。目标：425 及格。

## 核心交付（03-analysis/）

| 文件 | 内容 |
|------|------|
| **逆向复习手册.md** | 最终整合版：各模块可操作结论 + 考前 7 天背诵清单，**从这里开始读** |
| analysis_report.md | 阅读三模块的分布统计（答案分布/选项特征/重合率） |
| secC_reverse.md | 仔细阅读逆向：来源句定位（84%）、题文同序（τ=0.604）、改写强度、20 组替换对 |
| secAB_reverse.md | 选词填空词性规律 + 段落匹配顺序量化 + 同源替换对 |
| writing_translation_reverse.md | 写作 9 句万能骨架 + 翻译话题分布（75% 发展成就）与保命句型 7 条 |
| secC_pairs_dump.txt | 120 题"定位句→正确选项"全量替换素材 |
| secC_detail.csv / secA_detail.csv / secB_detail.csv | 逐题明细 |

## 核心结论速览

- **Section C**：答案来源句全文均匀分布，但题文强同序（第 n 题去全文 (n-1)/5~n/5 区段找）；正确选项是深度改写（62% 新词），词面重合高的选项反而危险（干扰项爱从别段搬词）。
- **Section B**：10 题永远对应 10 个不同段落（120/120 零例外）——排除法王牌；按序推进平均每题扫 2.8 段。
- **Section A**：词性只能排除不能锁定（过滤后中位剩 7 候选）；名词/动词/形容词占近 8 成。
- **写作**：第 1 句照抄题目句，9 句填空骨架覆盖 9/9 范文结构。
- **翻译**：近三期 75% 考"中国发展成就"叙事，传统历史文化题零命中；被动+such as+making 收尾即可及格。
- ⚠️ 机构答案键不可盲信：本项目修正了 xdf 聚合页 12 处 + NJU 解析 5 处答案错误（均经原文复核）。

## 目录结构

```
cet6-xiexiu/
├── 01-papers/       # 真题与解析 PDF（21 份；2025.06 三套为扫描件，靠 OCR 提取）
├── 02-parsed/       # PDF 导出文本 (*_raw.txt) + 结构化 JSON (parsed/)
├── 03-analysis/     # 分析报告与交付物（见上表）
├── scripts/         # 全部管线脚本（可重跑）
│   ├── parse_cet6.py        # PDF→JSON（答案键/词库/题目选项）
│   ├── analyze.py           # 分模块统计
│   ├── ocr_pdfs.py          # 扫描件 OCR（rapidocr）
│   ├── normalize_ocr.py     # OCR 文本归一化
│   ├── reverse_secC.py      # 逆向：来源句定位/同序/替换对
│   ├── reverse_secAB.py     # 逆向：词性/段落匹配
│   └── reverse_writing.py   # 逆向：写作/翻译模板
└── README.md
```

## 数据源

- GitHub [`0609x/CET46-Resources`](https://github.com/0609x/CET46-Resources)：2013–2026 真题与解析 PDF
- 南大 eol 站（eol.nju.edu.cn/cet6/papers/）：2024.12 解析文字层版
- 新东方 / koolearn / lazynote：答案键交叉验证（互相矛盾处一律以原文复核为准）

## 环境

- Python 3.13 + `.venv`（pymupdf、rapidocr-onnxruntime，不进 git）
- Windows / Git Bash

## 更新方式

1. 新考次 PDF 放入 `01-papers/`；扫描件跑 `scripts/ocr_pdfs.py`
2. 导出文本后，在 `scripts/parse_cet6.py` 的 `SETS` 注册并运行
3. `scripts/analyze.py` + `scripts/reverse_*.py` 重新生成全部报告
4. 答案键务必双源一致或原文复核后再入库
