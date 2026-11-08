# 数据层面归因（自动生成）

- 基模：`runs/eval-v1-nora-r16-20261106T121434+runs/eval-v1-nora-r16-retry1+runs/eval-v1-nora-r16-retry2+runs/eval-v1fill-nora-r16-20261106T151737+runs/eval-new-v2-nora-r16-20261106T142306`
- adapter：`runs/eval-full-r64-20261107T130258/2026-11-07__21-02-58+runs/eval-full-r64-rerun-k2/2026-11-07__22-25-55+runs/eval-full-r64-rerun-k1/2026-11-07__22-30-13`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 60.2 | 63.3 | +3.1 ±10.9 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 59.2 | 66.2 | +6.9 ±10.9 |
| 直接回答-知识直答 | 450 | 154 | 22 | 90.9 | 97.7 | +6.8 ±13.4 |
| 改文件写产物-代码 | 355 | 49 | 10 | 85.0 | 65.0 | -20.0 ±36.4 |
| 代码任务-Python | 317 | 29 | 46 | 65.2 | 54.3 | -10.9 ±12.2 |
| 代码任务-Node | 190 | 18 | 43 | 57.0 | 45.3 | -11.6 ±13.4 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 27.0 | 26.0 | -1.0 ±10.7 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 35.3 | 29.4 | -5.9 ±16.6 |
| 查找阅读-代码 | 116 | 22 | 84 | 48.8 | 49.4 | +0.6 ±7.9 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 40.5 | 52.4 | +11.9 ±21.3 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 54.6 | 50.8 | -3.8 ±12.6 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 37.5 | 50.0 | +12.5 ±24.5 |
| 直接回答-闲聊 | 81 | 22 | 13 | 76.9 | 84.6 | +7.7 ±18.7 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 74.3 | 75.7 | +1.4 ±13.6 |
| 改文件写产物-表格 | 72 | 10 | 9 | 55.6 | 66.7 | +11.1 ±42.5 |
| 统计计算-日志 | 71 | 10 | 22 | 20.5 | 22.7 | +2.3 ±12.0 |
| 外部信息-网络查询 | 69 | 10 | 86 | 88.4 | 86.6 | -1.7 ±8.0 |
| 统计计算-文件系统 | 69 | 10 | 8 | 75.0 | 75.0 | +0.0 ±32.1 |
| 查找阅读-日志 | 63 | 10 | 16 | 59.4 | 78.1 | +18.8 ±32.1 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 55.8 | 63.5 | +7.7 ±12.7 |
| 统计计算-表格 | 60 | 9 | 42 | 57.1 | 52.4 | -4.8 ±12.4 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 44.4 | 61.1 | +16.7 ±23.1 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 25.0 | 18.0 | -7.0 ±7.9 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 73.3 | 76.7 | +3.3 ±6.5 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 19.4 | 19.4 | +0.0 ±11.2 |
| 直接回答-做不到 | 25 | 7 | 17 | 35.3 | 55.9 | +20.6 ±22.3 |
| 改文件写产物-日志 | 5 | 1 | 2 | 50.0 | 50.0 | +0.0 ±0.0 |
| 统计计算-代码 | 5 | 2 | 2 | 0.0 | 50.0 | +50.0 ±98.0 |
| debugging | 0 | 0 | 40 | 50.0 | 38.8 | -11.2 ±13.4 |
| 直接回答-先答再查 | 0 | 0 | 23 | 69.6 | 69.6 | +0.0 ±23.9 |
| 终端操作-Shell | 0 | 0 | 60 | 10.8 | 13.3 | +2.5 ±7.9 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 50.0 | 38.8 | -11.2 ±13.4 |
| code-fix | heldout | 120 | 50.4 | 42.5 | -7.9 ±7.1 |
| code-fix | seen | 4 | 87.5 | 50.0 | -37.5 ±46.9 |
| direct | heldout | 71 | 69.0 | 76.1 | +7.0 ±10.5 |
| direct | seen | 4 | 75.0 | 100.0 | +25.0 ±49.0 |
| edit-code | heldout | 71 | 57.0 | 51.4 | -5.6 ±12.5 |
| edit-code | seen | 4 | 87.5 | 75.0 | -12.5 ±24.5 |
| edit-data | heldout | 71 | 50.7 | 59.9 | +9.2 ±11.2 |
| edit-data | seen | 4 | 87.5 | 87.5 | +0.0 ±40.0 |
| read-code | heldout | 80 | 47.5 | 48.1 | +0.6 ±8.3 |
| read-code | seen | 4 | 75.0 | 75.0 | +0.0 ±0.0 |
| read-local | heldout | 71 | 68.3 | 74.6 | +6.3 ±10.0 |
| read-local | seen | 4 | 50.0 | 75.0 | +25.0 ±49.0 |
| search | heldout | 107 | 79.0 | 79.9 | +0.9 ±7.7 |
| stat | heldout | 71 | 46.5 | 43.7 | -2.8 ±8.8 |
| stat | seen | 4 | 37.5 | 75.0 | +37.5 ±46.9 |
| terminal | heldout | 60 | 10.8 | 13.3 | +2.5 ±7.9 |
| web-code | heldout | 100 | 26.0 | 22.0 | -4.0 ±6.6 |
| web-local | heldout | 129 | 59.7 | 64.7 | +5.0 ±7.7 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（120 次失败）：tests-failed 78%, timeout 14%, answer-wrong 6%, no-required-tool 2%, wrote-in-read-only-turn 1%
- **code-fix** adapter（128 次失败）：tests-failed 86%, answer-wrong 7%, no-required-tool 5%, timeout 2%
- **code-fix-oss** base（40 次失败）：tests-failed 95%, timeout 5%
- **code-fix-oss** adapter（49 次失败）：tests-failed 100%
- **direct** base（46 次失败）：answer-wrong 54%, tools-when-none-needed 41%, used-forbidden-tool 4%
- **direct** adapter（34 次失败）：tools-when-none-needed 53%, answer-wrong 47%
- **edit-code** base（62 次失败）：answer-wrong 61%, file-result-wrong 31%, used-forbidden-tool 3%, too-many-calls 3%, timeout 2%
- **edit-code** adapter（70 次失败）：answer-wrong 54%, file-result-wrong 30%, too-many-calls 11%, used-forbidden-tool 3%, timeout 1%
- **edit-data** base（71 次失败）：file-result-wrong 56%, answer-wrong 44%
- **edit-data** adapter（58 次失败）：file-result-wrong 52%, answer-wrong 45%, too-many-calls 3%
- **read-code** base（86 次失败）：answer-wrong 58%, no-required-tool 34%, other 7%, wrote-in-read-only-turn 1%
- **read-code** adapter（85 次失败）：answer-wrong 60%, no-required-tool 35%, other 5%
- **read-local** base（49 次失败）：answer-wrong 94%, no-required-tool 4%, used-forbidden-tool 2%
- **read-local** adapter（38 次失败）：answer-wrong 97%, no-required-tool 3%
- **search** base（45 次失败）：no-web-search 69%, answer-wrong 27%, file-result-wrong 4%
- **search** adapter（43 次失败）：no-web-search 53%, answer-wrong 28%, file-result-wrong 14%, tests-failed 5%
- **stat** base（81 次失败）：answer-wrong 74%, timeout 23%, tools-when-none-needed 2%
- **stat** adapter（81 次失败）：answer-wrong 96%, tools-when-none-needed 2%, timeout 1%
- **terminal** base（107 次失败）：tests-failed 56%, file-result-wrong 30%, timeout 13%, answer-wrong 1%
- **terminal** adapter（106 次失败）：tests-failed 42%, timeout 32%, file-result-wrong 25%
- **web-code** base（149 次失败）：tests-failed 64%, timeout 17%, no-web-fetch 9%, wrote-in-read-only-turn 5%, no-required-tool 4%
- **web-code** adapter（156 次失败）：tests-failed 51%, timeout 31%, no-required-tool 15%, no-web-fetch 3%
- **web-local** base（104 次失败）：file-result-wrong 47%, answer-wrong 25%, no-required-tool 9%, tests-failed 8%, other 6%
- **web-local** adapter（91 次失败）：file-result-wrong 44%, answer-wrong 31%, tests-failed 12%, no-required-tool 7%, other 5%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 0% | 9.9 | 8% | 7% | - | - | - |
| code-fix | adapter | 0% | 10.3 | 9% | 11% | - | - | - |
| code-fix-oss | base | 0% | 4.3 | 7% | 0% | - | - | - |
| code-fix-oss | adapter | 0% | 4.6 | 7% | 7% | - | - | - |
| direct | base | 58% | 1.3 | 4% | 0% | - | - | - |
| direct | adapter | 63% | 1.1 | 2% | 0% | - | - | - |
| edit-code | base | 0% | 4.5 | 6% | 16% | - | - | - |
| edit-code | adapter | 0% | 5.1 | 7% | 24% | - | - | - |
| edit-data | base | 0% | 3.8 | 7% | 6% | - | - | - |
| edit-data | adapter | 0% | 4.1 | 5% | 11% | - | - | - |
| read-code | base | 0% | 4.9 | 4% | 2% | - | - | - |
| read-code | adapter | 0% | 5.4 | 4% | 1% | - | - | - |
| read-local | base | 2% | 2.5 | 1% | 2% | - | - | - |
| read-local | adapter | 0% | 2.7 | 1% | 0% | - | - | - |
| search | base | 3% | 2.5 | 9% | 0% | - | - | - |
| search | adapter | 5% | 2.7 | 9% | 1% | - | - | - |
| stat | base | 1% | 3.2 | 0% | 1% | - | - | - |
| stat | adapter | 1% | 3.0 | 2% | 2% | - | - | - |
| terminal | base | 0% | 9.7 | 5% | 2% | - | - | - |
| terminal | adapter | 0% | 9.5 | 5% | 6% | - | - | - |
| web-code | base | 0% | 9.5 | 10% | 5% | 99.0 | 5.5 | 0.03 |
| web-code | adapter | 0% | 8.9 | 10% | 8% | 99.5 | 9.5 | 0.02 |
| web-local | base | 0% | 5.3 | 10% | 4% | 98.8 | 6.6 | 0.01 |
| web-local | adapter | 0% | 5.7 | 6% | 10% | 100.0 | 7.4 | 0.0 |

## 变化最大的题（|差| ≥ 0.5，共 341 道；完整列表见 JSON）

- cfg-31007（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-35305（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-35354（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-35357（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-new-010（代码任务-Python，seen）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- doc-27353（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-35350（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- doc-35506（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33703（统计计算-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-120（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-128（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-13（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-136（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-140（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-33332（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-33380（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-33442（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35211（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 1, 'file-result-wrong': 1}
- hyb-35221（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35223（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35232（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35234（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35241（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- live-a-157（外部信息-真实网页-Coding验收，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 1, 'no-required-tool': 1}
- live-b-107（外部信息-真实网页-系统与数据，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 1, 'file-result-wrong': 1}
- …
- own-dr-053（直接回答-先答再查，heldout）：0.0 → 100.0；adapter 失败：-
- own-dr-055（直接回答-先答再查，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-044（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-051（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-023（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-045（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-076（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-096（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-104（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-109（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-tm-025（终端操作-Shell，heldout）：0.0 → 100.0；adapter 失败：-
- own-tm-047（终端操作-Shell，heldout）：0.0 → 100.0；adapter 失败：{'timeout': 2}
- own-wc-048（外部信息-真实网页-Coding混合，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-059（外部信息-真实网页-Coding验收，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-008（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-013（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-026（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-037（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-062（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31042（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31115（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32003（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32307（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- web-33076（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- web-34140（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
