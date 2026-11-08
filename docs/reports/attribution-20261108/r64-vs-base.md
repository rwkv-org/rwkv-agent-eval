# 数据层面归因（自动生成）

- 基模：`runs/eval-v1-base-20261106T133528+runs/eval-v1-base-retry1+runs/eval-v1-base-retry2+runs/eval-v1fill-base-20261106T145050+runs/eval-new-v2-base-20261106T142051`
- adapter：`runs/eval-full-r64-20261107T130258/2026-11-07__21-02-58+runs/eval-full-r64-rerun-k2/2026-11-07__22-25-55+runs/eval-full-r64-rerun-k1/2026-11-07__22-30-13`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 2.3 | 63.3 | +60.9 ±11.0 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 4.6 | 66.2 | +61.5 ±10.5 |
| 直接回答-知识直答 | 450 | 154 | 22 | 88.6 | 97.7 | +9.1 ±10.5 |
| 改文件写产物-代码 | 355 | 49 | 10 | 75.0 | 65.0 | -10.0 ±43.3 |
| 代码任务-Python | 317 | 29 | 46 | 22.8 | 54.3 | +31.5 ±15.6 |
| 代码任务-Node | 190 | 18 | 43 | 17.4 | 45.3 | +27.9 ±17.3 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 2.0 | 26.0 | +24.0 ±10.6 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 5.9 | 29.4 | +23.5 ±19.0 |
| 查找阅读-代码 | 116 | 22 | 84 | 39.9 | 49.4 | +9.5 ±11.2 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 4.8 | 52.4 | +47.6 ±19.7 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 40.8 | 50.8 | +10.0 ±14.4 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 8.3 | 50.0 | +41.7 ±31.5 |
| 直接回答-闲聊 | 81 | 22 | 13 | 80.8 | 84.6 | +3.8 ±25.9 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 45.7 | 75.7 | +30.0 ±23.8 |
| 改文件写产物-表格 | 72 | 10 | 9 | 16.7 | 66.7 | +50.0 ±23.1 |
| 统计计算-日志 | 71 | 10 | 22 | 15.9 | 22.7 | +6.8 ±13.4 |
| 外部信息-网络查询 | 69 | 10 | 86 | 76.2 | 86.6 | +10.5 ±8.7 |
| 统计计算-文件系统 | 69 | 10 | 8 | 37.5 | 75.0 | +37.5 ±35.9 |
| 查找阅读-日志 | 63 | 10 | 16 | 56.2 | 78.1 | +21.9 ±25.3 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 53.8 | 63.5 | +9.6 ±14.0 |
| 统计计算-表格 | 60 | 9 | 42 | 41.7 | 52.4 | +10.7 ±17.8 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 22.2 | 61.1 | +38.9 ±27.2 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 0.0 | 18.0 | +18.0 ±9.6 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 56.7 | 76.7 | +20.0 ±32.9 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 0.0 | 19.4 | +19.4 ±16.1 |
| 直接回答-做不到 | 25 | 7 | 17 | 50.0 | 55.9 | +5.9 ±31.3 |
| 改文件写产物-日志 | 5 | 1 | 2 | 100.0 | 50.0 | -50.0 ±98.0 |
| 统计计算-代码 | 5 | 2 | 2 | 75.0 | 50.0 | -25.0 ±147.0 |
| debugging | 0 | 0 | 40 | 37.5 | 38.8 | +1.2 ±18.4 |
| 直接回答-先答再查 | 0 | 0 | 23 | 41.3 | 69.6 | +28.3 ±20.3 |
| 终端操作-Shell | 0 | 0 | 60 | 0.0 | 13.3 | +13.3 ±7.3 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 37.5 | 38.8 | +1.2 ±18.4 |
| code-fix | heldout | 120 | 15.8 | 42.5 | +26.7 ±9.1 |
| code-fix | seen | 4 | 0.0 | 50.0 | +50.0 ±56.6 |
| direct | heldout | 71 | 63.4 | 76.1 | +12.7 ±11.2 |
| direct | seen | 4 | 75.0 | 100.0 | +25.0 ±49.0 |
| edit-code | heldout | 71 | 43.7 | 51.4 | +7.7 ±14.0 |
| edit-code | seen | 4 | 75.0 | 75.0 | +0.0 ±80.0 |
| edit-data | heldout | 71 | 43.0 | 59.9 | +16.9 ±12.6 |
| edit-data | seen | 4 | 50.0 | 87.5 | +37.5 ±46.9 |
| read-code | heldout | 80 | 41.9 | 48.1 | +6.2 ±11.1 |
| read-code | seen | 4 | 0.0 | 75.0 | +75.0 ±49.0 |
| read-local | heldout | 71 | 47.9 | 74.6 | +26.8 ±14.8 |
| read-local | seen | 4 | 37.5 | 75.0 | +37.5 ±46.9 |
| search | heldout | 107 | 62.1 | 79.9 | +17.8 ±8.5 |
| stat | heldout | 71 | 32.4 | 43.7 | +11.3 ±12.5 |
| stat | seen | 4 | 62.5 | 75.0 | +12.5 ±24.5 |
| terminal | heldout | 60 | 0.0 | 13.3 | +13.3 ±7.3 |
| web-code | heldout | 100 | 1.0 | 22.0 | +21.0 ±7.1 |
| web-local | heldout | 129 | 3.5 | 64.7 | +61.2 ±7.6 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（210 次失败）：tests-failed 59%, no-required-tool 39%, answer-wrong 1%, wrote-in-read-only-turn 0%, timeout 0%
- **code-fix** adapter（128 次失败）：tests-failed 86%, answer-wrong 7%, no-required-tool 5%, timeout 2%
- **code-fix-oss** base（50 次失败）：tests-failed 100%
- **code-fix-oss** adapter（49 次失败）：tests-failed 100%
- **direct** base（54 次失败）：tools-when-none-needed 57%, answer-wrong 31%, no-required-tool 4%, used-forbidden-tool 4%, wrote-in-read-only-turn 4%
- **direct** adapter（34 次失败）：tools-when-none-needed 53%, answer-wrong 47%
- **edit-code** base（82 次失败）：answer-wrong 66%, file-result-wrong 32%, used-forbidden-tool 2%
- **edit-code** adapter（70 次失败）：answer-wrong 54%, file-result-wrong 30%, too-many-calls 11%, used-forbidden-tool 3%, timeout 1%
- **edit-data** base（85 次失败）：file-result-wrong 55%, answer-wrong 42%, used-forbidden-tool 2%
- **edit-data** adapter（58 次失败）：file-result-wrong 52%, answer-wrong 45%, too-many-calls 3%
- **read-code** base（101 次失败）：answer-wrong 53%, no-required-tool 25%, wrote-in-read-only-turn 10%, other 10%, too-many-calls 2%
- **read-code** adapter（85 次失败）：answer-wrong 60%, no-required-tool 35%, other 5%
- **read-local** base（79 次失败）：answer-wrong 77%, no-required-tool 13%, used-forbidden-tool 6%, too-many-calls 3%, timeout 1%
- **read-local** adapter（38 次失败）：answer-wrong 97%, no-required-tool 3%
- **search** base（81 次失败）：answer-wrong 42%, no-web-search 31%, file-result-wrong 12%, used-forbidden-tool 9%, wrote-in-read-only-turn 4%
- **search** adapter（43 次失败）：no-web-search 53%, answer-wrong 28%, file-result-wrong 14%, tests-failed 5%
- **stat** base（99 次失败）：answer-wrong 90%, no-required-tool 6%, tools-when-none-needed 2%, timeout 2%
- **stat** adapter（81 次失败）：answer-wrong 96%, tools-when-none-needed 2%, timeout 1%
- **terminal** base（120 次失败）：tests-failed 57%, file-result-wrong 33%, no-required-tool 8%, answer-wrong 1%, timeout 1%
- **terminal** adapter（106 次失败）：tests-failed 42%, timeout 32%, file-result-wrong 25%
- **web-code** base（198 次失败）：no-web-fetch 76%, tests-failed 16%, no-required-tool 7%, wrote-in-read-only-turn 1%
- **web-code** adapter（156 次失败）：tests-failed 51%, timeout 31%, no-required-tool 15%, no-web-fetch 3%
- **web-local** base（249 次失败）：no-web-fetch 70%, no-required-tool 13%, answer-wrong 7%, file-result-wrong 6%, tests-failed 3%
- **web-local** adapter（91 次失败）：file-result-wrong 44%, answer-wrong 31%, tests-failed 12%, no-required-tool 7%, other 5%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 19% | 7.3 | 22% | 20% | - | - | - |
| code-fix | adapter | 0% | 10.3 | 9% | 11% | - | - | - |
| code-fix-oss | base | 8% | 2.8 | 8% | 1% | - | - | - |
| code-fix-oss | adapter | 0% | 4.6 | 7% | 7% | - | - | - |
| direct | base | 50% | 1.8 | 10% | 4% | - | - | - |
| direct | adapter | 63% | 1.1 | 2% | 0% | - | - | - |
| edit-code | base | 3% | 6.2 | 7% | 18% | - | - | - |
| edit-code | adapter | 0% | 5.1 | 7% | 24% | - | - | - |
| edit-data | base | 7% | 4.8 | 10% | 9% | - | - | - |
| edit-data | adapter | 0% | 4.1 | 5% | 11% | - | - | - |
| read-code | base | 10% | 7.0 | 12% | 14% | - | - | - |
| read-code | adapter | 0% | 5.4 | 4% | 1% | - | - | - |
| read-local | base | 1% | 4.9 | 8% | 5% | - | - | - |
| read-local | adapter | 0% | 2.7 | 1% | 0% | - | - | - |
| search | base | 4% | 3.7 | 14% | 3% | - | - | - |
| search | adapter | 5% | 2.7 | 9% | 1% | - | - | - |
| stat | base | 3% | 4.3 | 3% | 6% | - | - | - |
| stat | adapter | 1% | 3.0 | 2% | 2% | - | - | - |
| terminal | base | 6% | 7.3 | 4% | 4% | - | - | - |
| terminal | adapter | 0% | 9.5 | 5% | 6% | - | - | - |
| web-code | base | 39% | 3.1 | 22% | 9% | 27.0 | 7.5 | 0.18 |
| web-code | adapter | 0% | 8.9 | 10% | 8% | 99.5 | 9.5 | 0.02 |
| web-local | base | 28% | 3.7 | 42% | 14% | 34.9 | 36.4 | 0.12 |
| web-local | adapter | 0% | 5.7 | 6% | 10% | 100.0 | 7.4 | 0.0 |

## 变化最大的题（|差| ≥ 0.5，共 472 道；完整列表见 JSON）

- cfg-20135（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- cfg-27130（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-31007（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-35305（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-25034（统计计算-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-33525（改文件写产物-代码，seen）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-35354（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-35357（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- doc-27353（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-31379（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-31412（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-33268（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-35350（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- doc-35506（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-31230（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33722（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-120（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-136（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-140（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-25（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-65（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-31169（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-31174（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-33663（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35166（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- …
- own-wl-057（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-059（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-062（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-063（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-064（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-065（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-066（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-067（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-068（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-069（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-071（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-072（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-076（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-078（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-080（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-25006（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31029（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31115（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31406（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32003（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32025（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32207（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32212（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32307（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32314（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
