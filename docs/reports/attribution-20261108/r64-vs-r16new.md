# 数据层面归因（自动生成）

- 基模：`runs/eval-full-r16-20261107T150810/2026-11-07__23-08-10`
- adapter：`runs/eval-full-r64-20261107T130258/2026-11-07__21-02-58+runs/eval-full-r64-rerun-k2/2026-11-07__22-25-55+runs/eval-full-r64-rerun-k1/2026-11-07__22-30-13`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 62.5 | 63.3 | +0.8 ±11.2 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 59.2 | 66.2 | +6.9 ±9.8 |
| 直接回答-知识直答 | 450 | 154 | 22 | 90.9 | 97.7 | +6.8 ±13.4 |
| 改文件写产物-代码 | 355 | 49 | 10 | 80.0 | 65.0 | -15.0 ±20.9 |
| 代码任务-Python | 317 | 29 | 46 | 57.6 | 54.3 | -3.3 ±12.7 |
| 代码任务-Node | 190 | 18 | 43 | 51.2 | 45.3 | -5.8 ±15.4 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 29.0 | 26.0 | -3.0 ±11.0 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 32.4 | 29.4 | -2.9 ±13.2 |
| 查找阅读-代码 | 116 | 22 | 84 | 51.8 | 49.4 | -2.4 ±7.8 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 38.1 | 52.4 | +14.3 ±18.1 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 60.0 | 50.8 | -9.2 ±11.9 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 45.8 | 50.0 | +4.2 ±22.4 |
| 直接回答-闲聊 | 81 | 22 | 13 | 80.8 | 84.6 | +3.8 ±13.4 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 72.9 | 75.7 | +2.9 ±12.0 |
| 改文件写产物-表格 | 72 | 10 | 9 | 44.4 | 66.7 | +22.2 ±33.1 |
| 统计计算-日志 | 71 | 10 | 22 | 15.9 | 22.7 | +6.8 ±11.7 |
| 外部信息-网络查询 | 69 | 10 | 86 | 86.0 | 86.6 | +0.6 ±7.7 |
| 统计计算-文件系统 | 69 | 10 | 8 | 81.2 | 75.0 | -6.2 ±28.9 |
| 查找阅读-日志 | 63 | 10 | 16 | 62.5 | 78.1 | +15.6 ±29.3 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 51.9 | 63.5 | +11.5 ±11.3 |
| 统计计算-表格 | 60 | 9 | 42 | 48.8 | 52.4 | +3.6 ±14.3 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 61.1 | 61.1 | +0.0 ±16.3 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 23.0 | 18.0 | -5.0 ±8.0 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 76.7 | 76.7 | +0.0 ±9.6 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 25.0 | 19.4 | -5.6 ±19.2 |
| 直接回答-做不到 | 25 | 7 | 17 | 41.2 | 55.9 | +14.7 ±21.9 |
| 改文件写产物-日志 | 5 | 1 | 2 | 25.0 | 50.0 | +25.0 ±49.0 |
| 统计计算-代码 | 5 | 2 | 2 | 25.0 | 50.0 | +25.0 ±49.0 |
| debugging | 0 | 0 | 40 | 45.0 | 38.8 | -6.2 ±13.2 |
| 直接回答-先答再查 | 0 | 0 | 23 | 63.0 | 69.6 | +6.5 ±18.8 |
| 终端操作-Shell | 0 | 0 | 60 | 12.5 | 13.3 | +0.8 ±7.9 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 45.0 | 38.8 | -6.2 ±13.2 |
| code-fix | heldout | 120 | 45.8 | 42.5 | -3.3 ±7.8 |
| code-fix | seen | 4 | 87.5 | 50.0 | -37.5 ±46.9 |
| direct | heldout | 71 | 68.3 | 76.1 | +7.7 ±9.1 |
| direct | seen | 4 | 87.5 | 100.0 | +12.5 ±24.5 |
| edit-code | heldout | 71 | 60.6 | 51.4 | -9.2 ±11.0 |
| edit-code | seen | 4 | 100.0 | 75.0 | -25.0 ±49.0 |
| edit-data | heldout | 71 | 49.3 | 59.9 | +10.6 ±9.4 |
| edit-data | seen | 4 | 50.0 | 87.5 | +37.5 ±61.7 |
| read-code | heldout | 80 | 50.6 | 48.1 | -2.5 ±8.2 |
| read-code | seen | 4 | 75.0 | 75.0 | +0.0 ±0.0 |
| read-local | heldout | 71 | 69.7 | 74.6 | +4.9 ±9.3 |
| read-local | seen | 4 | 75.0 | 75.0 | +0.0 ±0.0 |
| search | heldout | 107 | 76.6 | 79.9 | +3.3 ±7.2 |
| stat | heldout | 71 | 40.1 | 43.7 | +3.5 ±9.7 |
| stat | seen | 4 | 62.5 | 75.0 | +12.5 ±24.5 |
| terminal | heldout | 60 | 12.5 | 13.3 | +0.8 ±7.9 |
| web-code | heldout | 100 | 26.0 | 22.0 | -4.0 ±6.8 |
| web-local | heldout | 129 | 60.9 | 64.7 | +3.9 ±7.4 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（131 次失败）：tests-failed 62%, timeout 31%, answer-wrong 5%, no-required-tool 2%, wrote-in-read-only-turn 1%
- **code-fix** adapter（128 次失败）：tests-failed 86%, answer-wrong 7%, no-required-tool 5%, timeout 2%
- **code-fix-oss** base（45 次失败）：tests-failed 84%, timeout 16%
- **code-fix-oss** adapter（49 次失败）：tests-failed 100%
- **direct** base（46 次失败）：answer-wrong 52%, tools-when-none-needed 46%, used-forbidden-tool 2%
- **direct** adapter（34 次失败）：tools-when-none-needed 53%, answer-wrong 47%
- **edit-code** base（56 次失败）：answer-wrong 41%, file-result-wrong 34%, too-many-calls 11%, timeout 7%, used-forbidden-tool 4%
- **edit-code** adapter（70 次失败）：answer-wrong 54%, file-result-wrong 30%, too-many-calls 11%, used-forbidden-tool 3%, timeout 1%
- **edit-data** base（76 次失败）：file-result-wrong 62%, answer-wrong 34%, too-many-calls 4%
- **edit-data** adapter（58 次失败）：file-result-wrong 52%, answer-wrong 45%, too-many-calls 3%
- **read-code** base（81 次失败）：answer-wrong 63%, no-required-tool 30%, other 7%
- **read-code** adapter（85 次失败）：answer-wrong 60%, no-required-tool 35%, other 5%
- **read-local** base（45 次失败）：answer-wrong 98%, no-required-tool 2%
- **read-local** adapter（38 次失败）：answer-wrong 97%, no-required-tool 3%
- **search** base（50 次失败）：no-web-search 56%, answer-wrong 34%, file-result-wrong 6%, too-many-calls 2%, timeout 2%
- **search** adapter（43 次失败）：no-web-search 53%, answer-wrong 28%, file-result-wrong 14%, tests-failed 5%
- **stat** base（88 次失败）：answer-wrong 75%, timeout 23%, tools-when-none-needed 2%
- **stat** adapter（81 次失败）：answer-wrong 96%, tools-when-none-needed 2%, timeout 1%
- **terminal** base（106 次失败）：tests-failed 42%, file-result-wrong 29%, timeout 27%, answer-wrong 1%
- **terminal** adapter（106 次失败）：tests-failed 42%, timeout 32%, file-result-wrong 25%
- **web-code** base（148 次失败）：tests-failed 43%, timeout 40%, no-web-fetch 9%, no-required-tool 7%, file-result-wrong 1%
- **web-code** adapter（156 次失败）：tests-failed 51%, timeout 31%, no-required-tool 15%, no-web-fetch 3%
- **web-local** base（101 次失败）：file-result-wrong 44%, answer-wrong 33%, other 7%, tests-failed 7%, no-required-tool 5%
- **web-local** adapter（91 次失败）：file-result-wrong 44%, answer-wrong 31%, tests-failed 12%, no-required-tool 7%, other 5%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 0% | 11.1 | 9% | 13% | - | - | - |
| code-fix | adapter | 0% | 10.3 | 9% | 11% | - | - | - |
| code-fix-oss | base | 0% | 5.2 | 7% | 7% | - | - | - |
| code-fix-oss | adapter | 0% | 4.6 | 7% | 7% | - | - | - |
| direct | base | 59% | 1.2 | 3% | 0% | - | - | - |
| direct | adapter | 63% | 1.1 | 2% | 0% | - | - | - |
| edit-code | base | 0% | 5.1 | 6% | 25% | - | - | - |
| edit-code | adapter | 0% | 5.1 | 7% | 24% | - | - | - |
| edit-data | base | 0% | 4.2 | 5% | 12% | - | - | - |
| edit-data | adapter | 0% | 4.1 | 5% | 11% | - | - | - |
| read-code | base | 0% | 5.2 | 4% | 2% | - | - | - |
| read-code | adapter | 0% | 5.4 | 4% | 1% | - | - | - |
| read-local | base | 2% | 2.4 | 1% | 1% | - | - | - |
| read-local | adapter | 0% | 2.7 | 1% | 0% | - | - | - |
| search | base | 3% | 2.6 | 9% | 1% | - | - | - |
| search | adapter | 5% | 2.7 | 9% | 1% | - | - | - |
| stat | base | 1% | 3.2 | 0% | 1% | - | - | - |
| stat | adapter | 1% | 3.0 | 2% | 2% | - | - | - |
| terminal | base | 0% | 9.9 | 5% | 7% | - | - | - |
| terminal | adapter | 0% | 9.5 | 5% | 6% | - | - | - |
| web-code | base | 0% | 10.0 | 10% | 9% | 98.5 | 8.0 | 0.09 |
| web-code | adapter | 0% | 8.9 | 10% | 8% | 99.5 | 9.5 | 0.02 |
| web-local | base | 0% | 5.8 | 9% | 10% | 99.6 | 7.8 | 0.01 |
| web-local | adapter | 0% | 5.7 | 6% | 10% | 100.0 | 7.4 | 0.0 |

## 变化最大的题（|差| ≥ 0.5，共 319 道；完整列表见 JSON）

- cfg-35305（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-33525（改文件写产物-代码，seen）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-new-010（代码任务-Python，seen）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- doc-27353（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-35506（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33703（统计计算-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-120（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-136（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-42（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-69（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-33332（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-33380（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-33442（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35165（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35211（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 1, 'file-result-wrong': 1}
- hyb-35218（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35223（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35232（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35234（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- live-a-144（外部信息-真实网页-编程文档，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- live-a-157（外部信息-真实网页-Coding验收，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 1, 'no-required-tool': 1}
- live-b-146（外部信息-真实网页-系统与数据，heldout）：100.0 → 0.0；adapter 失败：{'no-required-tool': 2}
- log-34409（查找阅读-日志，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-cf-017（代码任务-Node，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- own-cf-022（代码任务-Node，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- …
- own-dr-056（直接回答-先答再查，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-019（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-044（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-051（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-023（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-036（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-045（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-076（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-097（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-098（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-104（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-tm-025（终端操作-Shell，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-059（外部信息-真实网页-Coding验收，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-008（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-013（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-026（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-037（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-062（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-063（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-20112（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31042（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31115（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32003（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32307（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- web-33076（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
