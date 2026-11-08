# 数据层面归因（自动生成）

- 基模：`runs/eval-v1-base-20261106T133528+runs/eval-v1-base-retry1+runs/eval-v1-base-retry2+runs/eval-v1fill-base-20261106T145050+runs/eval-new-v2-base-20261106T142051`
- adapter：`runs/eval-full-r16-20261107T150810/2026-11-07__23-08-10`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 2.3 | 62.5 | +60.2 ±11.2 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 4.6 | 59.2 | +54.6 ±10.7 |
| 直接回答-知识直答 | 450 | 154 | 22 | 88.6 | 90.9 | +2.3 ±18.8 |
| 改文件写产物-代码 | 355 | 49 | 10 | 75.0 | 80.0 | +5.0 ±42.5 |
| 代码任务-Python | 317 | 29 | 46 | 22.8 | 57.6 | +34.8 ±15.8 |
| 代码任务-Node | 190 | 18 | 43 | 17.4 | 51.2 | +33.7 ±16.2 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 2.0 | 29.0 | +27.0 ±10.6 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 5.9 | 32.4 | +26.5 ±19.0 |
| 查找阅读-代码 | 116 | 22 | 84 | 39.9 | 51.8 | +11.9 ±11.5 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 4.8 | 38.1 | +33.3 ±19.5 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 40.8 | 60.0 | +19.2 ±15.4 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 8.3 | 45.8 | +37.5 ±27.3 |
| 直接回答-闲聊 | 81 | 22 | 13 | 80.8 | 80.8 | +0.0 ±27.2 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 45.7 | 72.9 | +27.1 ±22.1 |
| 改文件写产物-表格 | 72 | 10 | 9 | 16.7 | 44.4 | +27.8 ±33.1 |
| 统计计算-日志 | 71 | 10 | 22 | 15.9 | 15.9 | +0.0 ±12.9 |
| 外部信息-网络查询 | 69 | 10 | 86 | 76.2 | 86.0 | +9.9 ±8.7 |
| 统计计算-文件系统 | 69 | 10 | 8 | 37.5 | 81.2 | +43.8 ±43.2 |
| 查找阅读-日志 | 63 | 10 | 16 | 56.2 | 62.5 | +6.2 ±25.1 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 53.8 | 51.9 | -1.9 ±13.7 |
| 统计计算-表格 | 60 | 9 | 42 | 41.7 | 48.8 | +7.1 ±16.6 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 22.2 | 61.1 | +38.9 ±31.7 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 0.0 | 23.0 | +23.0 ±10.2 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 56.7 | 76.7 | +20.0 ±32.9 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 0.0 | 25.0 | +25.0 ±18.2 |
| 直接回答-做不到 | 25 | 7 | 17 | 50.0 | 41.2 | -8.8 ±21.0 |
| 改文件写产物-日志 | 5 | 1 | 2 | 100.0 | 25.0 | -75.0 ±49.0 |
| 统计计算-代码 | 5 | 2 | 2 | 75.0 | 25.0 | -50.0 ±98.0 |
| debugging | 0 | 0 | 40 | 37.5 | 45.0 | +7.5 ±18.7 |
| 直接回答-先答再查 | 0 | 0 | 23 | 41.3 | 63.0 | +21.7 ±22.9 |
| 终端操作-Shell | 0 | 0 | 60 | 0.0 | 12.5 | +12.5 ±7.2 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 37.5 | 45.0 | +7.5 ±18.7 |
| code-fix | heldout | 120 | 15.8 | 45.8 | +30.0 ±8.9 |
| code-fix | seen | 4 | 0.0 | 87.5 | +87.5 ±24.5 |
| direct | heldout | 71 | 63.4 | 68.3 | +4.9 ±11.8 |
| direct | seen | 4 | 75.0 | 87.5 | +12.5 ±24.5 |
| edit-code | heldout | 71 | 43.7 | 60.6 | +16.9 ±15.1 |
| edit-code | seen | 4 | 75.0 | 100.0 | +25.0 ±49.0 |
| edit-data | heldout | 71 | 43.0 | 49.3 | +6.3 ±12.3 |
| edit-data | seen | 4 | 50.0 | 50.0 | +0.0 ±69.3 |
| read-code | heldout | 80 | 41.9 | 50.6 | +8.8 ±11.4 |
| read-code | seen | 4 | 0.0 | 75.0 | +75.0 ±49.0 |
| read-local | heldout | 71 | 47.9 | 69.7 | +21.8 ±14.4 |
| read-local | seen | 4 | 37.5 | 75.0 | +37.5 ±46.9 |
| search | heldout | 107 | 62.1 | 76.6 | +14.5 ±8.1 |
| stat | heldout | 71 | 32.4 | 40.1 | +7.7 ±12.2 |
| stat | seen | 4 | 62.5 | 62.5 | +0.0 ±0.0 |
| terminal | heldout | 60 | 0.0 | 12.5 | +12.5 ±7.2 |
| web-code | heldout | 100 | 1.0 | 26.0 | +25.0 ±7.3 |
| web-local | heldout | 129 | 3.5 | 60.9 | +57.4 ±7.7 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（210 次失败）：tests-failed 59%, no-required-tool 39%, answer-wrong 1%, wrote-in-read-only-turn 0%, timeout 0%
- **code-fix** adapter（131 次失败）：tests-failed 62%, timeout 31%, answer-wrong 5%, no-required-tool 2%, wrote-in-read-only-turn 1%
- **code-fix-oss** base（50 次失败）：tests-failed 100%
- **code-fix-oss** adapter（45 次失败）：tests-failed 84%, timeout 16%
- **direct** base（54 次失败）：tools-when-none-needed 57%, answer-wrong 31%, no-required-tool 4%, used-forbidden-tool 4%, wrote-in-read-only-turn 4%
- **direct** adapter（46 次失败）：answer-wrong 52%, tools-when-none-needed 46%, used-forbidden-tool 2%
- **edit-code** base（82 次失败）：answer-wrong 66%, file-result-wrong 32%, used-forbidden-tool 2%
- **edit-code** adapter（56 次失败）：answer-wrong 41%, file-result-wrong 34%, too-many-calls 11%, timeout 7%, used-forbidden-tool 4%
- **edit-data** base（85 次失败）：file-result-wrong 55%, answer-wrong 42%, used-forbidden-tool 2%
- **edit-data** adapter（76 次失败）：file-result-wrong 62%, answer-wrong 34%, too-many-calls 4%
- **read-code** base（101 次失败）：answer-wrong 53%, no-required-tool 25%, wrote-in-read-only-turn 10%, other 10%, too-many-calls 2%
- **read-code** adapter（81 次失败）：answer-wrong 63%, no-required-tool 30%, other 7%
- **read-local** base（79 次失败）：answer-wrong 77%, no-required-tool 13%, used-forbidden-tool 6%, too-many-calls 3%, timeout 1%
- **read-local** adapter（45 次失败）：answer-wrong 98%, no-required-tool 2%
- **search** base（81 次失败）：answer-wrong 42%, no-web-search 31%, file-result-wrong 12%, used-forbidden-tool 9%, wrote-in-read-only-turn 4%
- **search** adapter（50 次失败）：no-web-search 56%, answer-wrong 34%, file-result-wrong 6%, too-many-calls 2%, timeout 2%
- **stat** base（99 次失败）：answer-wrong 90%, no-required-tool 6%, tools-when-none-needed 2%, timeout 2%
- **stat** adapter（88 次失败）：answer-wrong 75%, timeout 23%, tools-when-none-needed 2%
- **terminal** base（120 次失败）：tests-failed 57%, file-result-wrong 33%, no-required-tool 8%, answer-wrong 1%, timeout 1%
- **terminal** adapter（106 次失败）：tests-failed 42%, file-result-wrong 29%, timeout 27%, answer-wrong 1%
- **web-code** base（198 次失败）：no-web-fetch 76%, tests-failed 16%, no-required-tool 7%, wrote-in-read-only-turn 1%
- **web-code** adapter（148 次失败）：tests-failed 43%, timeout 40%, no-web-fetch 9%, no-required-tool 7%, file-result-wrong 1%
- **web-local** base（249 次失败）：no-web-fetch 70%, no-required-tool 13%, answer-wrong 7%, file-result-wrong 6%, tests-failed 3%
- **web-local** adapter（101 次失败）：file-result-wrong 44%, answer-wrong 33%, other 7%, tests-failed 7%, no-required-tool 5%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 19% | 7.3 | 22% | 20% | - | - | - |
| code-fix | adapter | 0% | 11.1 | 9% | 13% | - | - | - |
| code-fix-oss | base | 8% | 2.8 | 8% | 1% | - | - | - |
| code-fix-oss | adapter | 0% | 5.2 | 7% | 7% | - | - | - |
| direct | base | 50% | 1.8 | 10% | 4% | - | - | - |
| direct | adapter | 59% | 1.2 | 3% | 0% | - | - | - |
| edit-code | base | 3% | 6.2 | 7% | 18% | - | - | - |
| edit-code | adapter | 0% | 5.1 | 6% | 25% | - | - | - |
| edit-data | base | 7% | 4.8 | 10% | 9% | - | - | - |
| edit-data | adapter | 0% | 4.2 | 5% | 12% | - | - | - |
| read-code | base | 10% | 7.0 | 12% | 14% | - | - | - |
| read-code | adapter | 0% | 5.2 | 4% | 2% | - | - | - |
| read-local | base | 1% | 4.9 | 8% | 5% | - | - | - |
| read-local | adapter | 2% | 2.4 | 1% | 1% | - | - | - |
| search | base | 4% | 3.7 | 14% | 3% | - | - | - |
| search | adapter | 3% | 2.6 | 9% | 1% | - | - | - |
| stat | base | 3% | 4.3 | 3% | 6% | - | - | - |
| stat | adapter | 1% | 3.2 | 0% | 1% | - | - | - |
| terminal | base | 6% | 7.3 | 4% | 4% | - | - | - |
| terminal | adapter | 0% | 9.9 | 5% | 7% | - | - | - |
| web-code | base | 39% | 3.1 | 22% | 9% | 27.0 | 7.5 | 0.18 |
| web-code | adapter | 0% | 10.0 | 10% | 9% | 98.5 | 8.0 | 0.09 |
| web-local | base | 28% | 3.7 | 42% | 14% | 34.9 | 36.4 | 0.12 |
| web-local | adapter | 0% | 5.8 | 9% | 10% | 99.6 | 7.8 | 0.01 |

## 变化最大的题（|差| ≥ 0.5，共 464 道；完整列表见 JSON）

- cfg-20135（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- cfg-27130（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-31007（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-31256（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-35306（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- cfg-35349（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-25034（统计计算-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-35354（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-35357（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- doc-27380（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- doc-31148（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- doc-31379（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-31412（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-33268（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-31230（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33722（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-131（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-135（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-25（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-65（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-71（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-31169（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-31174（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35163（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35166（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- …
- own-wl-046（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-048（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-052（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-055（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-056（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-059（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-065（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-066（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-067（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-068（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-069（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-071（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-072（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-075（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-076（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-078（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-080（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-25006（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31029（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31140（改文件写产物-表格，seen）：0.0 → 100.0；adapter 失败：-
- tab-31406（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32014（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32015（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32212（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32315（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
