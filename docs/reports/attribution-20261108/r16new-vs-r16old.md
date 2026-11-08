# 数据层面归因（自动生成）

- 基模：`runs/eval-v1-nora-r16-20261106T121434+runs/eval-v1-nora-r16-retry1+runs/eval-v1-nora-r16-retry2+runs/eval-v1fill-nora-r16-20261106T151737+runs/eval-new-v2-nora-r16-20261106T142306`
- adapter：`runs/eval-full-r16-20261107T150810/2026-11-07__23-08-10`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 60.2 | 62.5 | +2.3 ±7.0 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 59.2 | 59.2 | +0.0 ±8.0 |
| 直接回答-知识直答 | 450 | 154 | 22 | 90.9 | 90.9 | +0.0 ±0.0 |
| 改文件写产物-代码 | 355 | 49 | 10 | 85.0 | 80.0 | -5.0 ±37.1 |
| 代码任务-Python | 317 | 29 | 46 | 65.2 | 57.6 | -7.6 ±8.6 |
| 代码任务-Node | 190 | 18 | 43 | 57.0 | 51.2 | -5.8 ±11.9 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 27.0 | 29.0 | +2.0 ±7.9 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 35.3 | 32.4 | -2.9 ±13.2 |
| 查找阅读-代码 | 116 | 22 | 84 | 48.8 | 51.8 | +3.0 ±4.8 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 40.5 | 38.1 | -2.4 ±19.7 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 54.6 | 60.0 | +5.4 ±8.4 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 37.5 | 45.8 | +8.3 ±16.3 |
| 直接回答-闲聊 | 81 | 22 | 13 | 76.9 | 80.8 | +3.8 ±7.5 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 74.3 | 72.9 | -1.4 ±6.3 |
| 改文件写产物-表格 | 72 | 10 | 9 | 55.6 | 44.4 | -11.1 ±21.8 |
| 统计计算-日志 | 71 | 10 | 22 | 20.5 | 15.9 | -4.5 ±6.1 |
| 外部信息-网络查询 | 69 | 10 | 86 | 88.4 | 86.0 | -2.3 ±4.3 |
| 统计计算-文件系统 | 69 | 10 | 8 | 75.0 | 81.2 | +6.2 ±12.2 |
| 查找阅读-日志 | 63 | 10 | 16 | 59.4 | 62.5 | +3.1 ±16.7 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 55.8 | 51.9 | -3.8 ±9.3 |
| 统计计算-表格 | 60 | 9 | 42 | 57.1 | 48.8 | -8.3 ±11.0 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 44.4 | 61.1 | +16.7 ±28.3 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 25.0 | 23.0 | -2.0 ±7.9 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 73.3 | 76.7 | +3.3 ±6.5 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 19.4 | 25.0 | +5.6 ±13.5 |
| 直接回答-做不到 | 25 | 7 | 17 | 35.3 | 41.2 | +5.9 ±11.5 |
| 改文件写产物-日志 | 5 | 1 | 2 | 50.0 | 25.0 | -25.0 ±49.0 |
| 统计计算-代码 | 5 | 2 | 2 | 0.0 | 25.0 | +25.0 ±49.0 |
| debugging | 0 | 0 | 40 | 50.0 | 45.0 | -5.0 ±12.1 |
| 直接回答-先答再查 | 0 | 0 | 23 | 69.6 | 63.0 | -6.5 ±12.8 |
| 终端操作-Shell | 0 | 0 | 60 | 10.8 | 12.5 | +1.7 ±5.2 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 50.0 | 45.0 | -5.0 ±12.1 |
| code-fix | heldout | 120 | 50.4 | 45.8 | -4.6 ±6.0 |
| code-fix | seen | 4 | 87.5 | 87.5 | +0.0 ±0.0 |
| direct | heldout | 71 | 69.0 | 68.3 | -0.7 ±5.0 |
| direct | seen | 4 | 75.0 | 87.5 | +12.5 ±24.5 |
| edit-code | heldout | 71 | 57.0 | 60.6 | +3.5 ±9.1 |
| edit-code | seen | 4 | 87.5 | 100.0 | +12.5 ±24.5 |
| edit-data | heldout | 71 | 50.7 | 49.3 | -1.4 ±7.3 |
| edit-data | seen | 4 | 87.5 | 50.0 | -37.5 ±46.9 |
| read-code | heldout | 80 | 47.5 | 50.6 | +3.1 ±5.0 |
| read-code | seen | 4 | 75.0 | 75.0 | +0.0 ±0.0 |
| read-local | heldout | 71 | 68.3 | 69.7 | +1.4 ±5.6 |
| read-local | seen | 4 | 50.0 | 75.0 | +25.0 ±49.0 |
| search | heldout | 107 | 79.0 | 76.6 | -2.3 ±5.1 |
| stat | heldout | 71 | 46.5 | 40.1 | -6.3 ±6.8 |
| stat | seen | 4 | 37.5 | 62.5 | +25.0 ±28.3 |
| terminal | heldout | 60 | 10.8 | 12.5 | +1.7 ±5.2 |
| web-code | heldout | 100 | 26.0 | 26.0 | +0.0 ±5.6 |
| web-local | heldout | 129 | 59.7 | 60.9 | +1.2 ±5.3 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（120 次失败）：tests-failed 78%, timeout 14%, answer-wrong 6%, no-required-tool 2%, wrote-in-read-only-turn 1%
- **code-fix** adapter（131 次失败）：tests-failed 62%, timeout 31%, answer-wrong 5%, no-required-tool 2%, wrote-in-read-only-turn 1%
- **code-fix-oss** base（40 次失败）：tests-failed 95%, timeout 5%
- **code-fix-oss** adapter（45 次失败）：tests-failed 84%, timeout 16%
- **direct** base（46 次失败）：answer-wrong 54%, tools-when-none-needed 41%, used-forbidden-tool 4%
- **direct** adapter（46 次失败）：answer-wrong 52%, tools-when-none-needed 46%, used-forbidden-tool 2%
- **edit-code** base（62 次失败）：answer-wrong 61%, file-result-wrong 31%, used-forbidden-tool 3%, too-many-calls 3%, timeout 2%
- **edit-code** adapter（56 次失败）：answer-wrong 41%, file-result-wrong 34%, too-many-calls 11%, timeout 7%, used-forbidden-tool 4%
- **edit-data** base（71 次失败）：file-result-wrong 56%, answer-wrong 44%
- **edit-data** adapter（76 次失败）：file-result-wrong 62%, answer-wrong 34%, too-many-calls 4%
- **read-code** base（86 次失败）：answer-wrong 58%, no-required-tool 34%, other 7%, wrote-in-read-only-turn 1%
- **read-code** adapter（81 次失败）：answer-wrong 63%, no-required-tool 30%, other 7%
- **read-local** base（49 次失败）：answer-wrong 94%, no-required-tool 4%, used-forbidden-tool 2%
- **read-local** adapter（45 次失败）：answer-wrong 98%, no-required-tool 2%
- **search** base（45 次失败）：no-web-search 69%, answer-wrong 27%, file-result-wrong 4%
- **search** adapter（50 次失败）：no-web-search 56%, answer-wrong 34%, file-result-wrong 6%, too-many-calls 2%, timeout 2%
- **stat** base（81 次失败）：answer-wrong 74%, timeout 23%, tools-when-none-needed 2%
- **stat** adapter（88 次失败）：answer-wrong 75%, timeout 23%, tools-when-none-needed 2%
- **terminal** base（107 次失败）：tests-failed 56%, file-result-wrong 30%, timeout 13%, answer-wrong 1%
- **terminal** adapter（106 次失败）：tests-failed 42%, file-result-wrong 29%, timeout 27%, answer-wrong 1%
- **web-code** base（149 次失败）：tests-failed 64%, timeout 17%, no-web-fetch 9%, wrote-in-read-only-turn 5%, no-required-tool 4%
- **web-code** adapter（148 次失败）：tests-failed 43%, timeout 40%, no-web-fetch 9%, no-required-tool 7%, file-result-wrong 1%
- **web-local** base（104 次失败）：file-result-wrong 47%, answer-wrong 25%, no-required-tool 9%, tests-failed 8%, other 6%
- **web-local** adapter（101 次失败）：file-result-wrong 44%, answer-wrong 33%, other 7%, tests-failed 7%, no-required-tool 5%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 0% | 9.9 | 8% | 7% | - | - | - |
| code-fix | adapter | 0% | 11.1 | 9% | 13% | - | - | - |
| code-fix-oss | base | 0% | 4.3 | 7% | 0% | - | - | - |
| code-fix-oss | adapter | 0% | 5.2 | 7% | 7% | - | - | - |
| direct | base | 58% | 1.3 | 4% | 0% | - | - | - |
| direct | adapter | 59% | 1.2 | 3% | 0% | - | - | - |
| edit-code | base | 0% | 4.5 | 6% | 16% | - | - | - |
| edit-code | adapter | 0% | 5.1 | 6% | 25% | - | - | - |
| edit-data | base | 0% | 3.8 | 7% | 6% | - | - | - |
| edit-data | adapter | 0% | 4.2 | 5% | 12% | - | - | - |
| read-code | base | 0% | 4.9 | 4% | 2% | - | - | - |
| read-code | adapter | 0% | 5.2 | 4% | 2% | - | - | - |
| read-local | base | 2% | 2.5 | 1% | 2% | - | - | - |
| read-local | adapter | 2% | 2.4 | 1% | 1% | - | - | - |
| search | base | 3% | 2.5 | 9% | 0% | - | - | - |
| search | adapter | 3% | 2.6 | 9% | 1% | - | - | - |
| stat | base | 1% | 3.2 | 0% | 1% | - | - | - |
| stat | adapter | 1% | 3.2 | 0% | 1% | - | - | - |
| terminal | base | 0% | 9.7 | 5% | 2% | - | - | - |
| terminal | adapter | 0% | 9.9 | 5% | 7% | - | - | - |
| web-code | base | 0% | 9.5 | 10% | 5% | 99.0 | 5.5 | 0.03 |
| web-code | adapter | 0% | 10.0 | 10% | 9% | 98.5 | 8.0 | 0.09 |
| web-local | base | 0% | 5.3 | 10% | 4% | 98.8 | 6.6 | 0.01 |
| web-local | adapter | 0% | 5.8 | 9% | 10% | 99.6 | 7.8 | 0.01 |

## 变化最大的题（|差| ≥ 0.5，共 218 道；完整列表见 JSON）

- cfg-31007（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-35349（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-35354（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-35357（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-new-011（代码任务-Python，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- doc-20073（改文件写产物-文档配置，seen）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-111（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-128（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-90（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-35221（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35241（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-cf-024（代码任务-Node，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 1, 'no-required-tool': 1}
- own-cf-071（代码任务-Node，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- own-cf-090（代码任务-Python，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- own-cf-097（代码任务-Python-多模块，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- own-cf-108（代码任务-Node，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- own-se-036（外部信息-网络查询，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-se-099（外部信息-网络加本地，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-wl-063（外部信息-真实网页-系统与数据，heldout）：100.0 → 0.0；adapter 失败：{'no-required-tool': 1, 'answer-wrong': 1}
- tab-20112（统计计算-表格，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- tab-28056（直接回答-先答再查，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- tab-31118（改文件写产物-表格，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- tab-32206（统计计算-表格，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- tab-32236（统计计算-表格，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 1, 'timeout': 1}
- doc-27001（查找阅读-文档配置，heldout）：100.0 → 50.0；adapter 失败：{'answer-wrong': 1}
- …
- own-wl-076（外部信息-真实网页-系统与数据，heldout）：50.0 → 100.0；adapter 失败：-
- tab-32304（统计计算-表格，heldout）：50.0 → 100.0；adapter 失败：-
- tab-34428（统计计算-表格，heldout）：0.0 → 50.0；adapter 失败：{'answer-wrong': 1}
- cfg-31070（改文件写产物-文档配置，heldout）：0.0 → 100.0；adapter 失败：-
- code-31074（改文件写产物-代码，heldout）：0.0 → 100.0；adapter 失败：-
- doc-31152（改文件写产物-文档配置，heldout）：0.0 → 100.0；adapter 失败：-
- humanevalfix__python-42（debugging，oss）：0.0 → 100.0；adapter 失败：-
- hyb-25035（查找阅读-跨类混合，seen）：0.0 → 100.0；adapter 失败：-
- hyb-33458（改文件写产物-跨类混合，heldout）：0.0 → 100.0；adapter 失败：-
- hyb-35165（改文件写产物-跨类混合，heldout）：0.0 → 100.0；adapter 失败：-
- hyb-35218（改文件写产物-跨类混合，heldout）：0.0 → 100.0；adapter 失败：-
- hyb-35224（改文件写产物-跨类混合，heldout）：0.0 → 100.0；adapter 失败：-
- live-b-123（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- log-27615（查找阅读-日志，heldout）：0.0 → 100.0；adapter 失败：-
- own-cf-022（代码任务-Node，heldout）：0.0 → 100.0；adapter 失败：-
- own-cf-066（代码任务-Node，heldout）：0.0 → 100.0；adapter 失败：-
- own-cf-118（代码任务-Node-多模块，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-103（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-109（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-tm-023（终端操作-Shell，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-055（外部信息-真实网页-Coding验收，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-086（外部信息-真实网页-Coding混合，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-023（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32302（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- web-34140（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
