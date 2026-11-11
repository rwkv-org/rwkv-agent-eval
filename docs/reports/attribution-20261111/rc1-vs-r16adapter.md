# 数据层面归因（自动生成）

- 基模：`runs/eval-full-r16old-adapter-1111-20261111T073348/2026-11-11__15-33-48`
- adapter：`runs/eval-full-r16-261111-rc1-20261111T095533/2026-11-11__17-55-33`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 61.7 | 63.3 | +1.6 ±8.4 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 56.9 | 63.1 | +6.2 ±8.5 |
| 直接回答-知识直答 | 450 | 154 | 22 | 90.9 | 100.0 | +9.1 ±12.3 |
| 改文件写产物-代码 | 355 | 49 | 10 | 75.0 | 75.0 | +0.0 ±14.6 |
| 代码任务-Python | 317 | 29 | 46 | 65.2 | 71.7 | +6.5 ±10.4 |
| 代码任务-Node | 190 | 18 | 43 | 53.5 | 55.8 | +2.3 ±12.6 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 28.0 | 37.0 | +9.0 ±11.4 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 41.2 | 29.4 | -11.8 ±13.4 |
| 查找阅读-代码 | 116 | 22 | 84 | 53.6 | 56.5 | +3.0 ±8.0 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 45.2 | 57.1 | +11.9 ±21.3 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 56.2 | 60.0 | +3.8 ±12.2 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 41.7 | 66.7 | +25.0 ±28.3 |
| 直接回答-闲聊 | 81 | 22 | 13 | 80.8 | 80.8 | +0.0 ±19.2 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 71.4 | 68.6 | -2.9 ±17.5 |
| 改文件写产物-表格 | 72 | 10 | 9 | 44.4 | 66.7 | +22.2 ±40.4 |
| 统计计算-日志 | 71 | 10 | 22 | 22.7 | 34.1 | +11.4 ±15.7 |
| 外部信息-网络查询 | 69 | 10 | 86 | 86.0 | 89.5 | +3.5 ±6.2 |
| 统计计算-文件系统 | 69 | 10 | 8 | 68.8 | 62.5 | -6.2 ±39.0 |
| 查找阅读-日志 | 63 | 10 | 16 | 59.4 | 75.0 | +15.6 ±34.3 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 48.1 | 61.5 | +13.5 ±12.9 |
| 统计计算-表格 | 60 | 9 | 42 | 54.8 | 54.8 | +0.0 ±13.4 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 50.0 | 61.1 | +11.1 ±35.7 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 28.0 | 23.0 | -5.0 ±9.8 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 73.3 | 66.7 | -6.7 ±13.1 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 22.2 | 22.2 | +0.0 ±11.2 |
| 直接回答-做不到 | 25 | 7 | 17 | 44.1 | 41.2 | -2.9 ±21.4 |
| 改文件写产物-日志 | 5 | 1 | 2 | 25.0 | 50.0 | +25.0 ±49.0 |
| 统计计算-代码 | 5 | 2 | 2 | 0.0 | 50.0 | +50.0 ±98.0 |
| debugging | 0 | 0 | 40 | 48.8 | 58.8 | +10.0 ±15.0 |
| 直接回答-先答再查 | 0 | 0 | 23 | 67.4 | 78.3 | +10.9 ±20.4 |
| 终端操作-Shell | 0 | 0 | 60 | 17.5 | 11.7 | -5.8 ±6.2 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 48.8 | 58.8 | +10.0 ±15.0 |
| code-fix | heldout | 120 | 51.2 | 52.9 | +1.7 ±6.6 |
| code-fix | seen | 4 | 62.5 | 62.5 | +0.0 ±0.0 |
| direct | heldout | 71 | 70.4 | 75.4 | +4.9 ±9.7 |
| direct | seen | 4 | 87.5 | 100.0 | +12.5 ±24.5 |
| edit-code | heldout | 71 | 57.0 | 59.9 | +2.8 ±11.3 |
| edit-code | seen | 4 | 87.5 | 100.0 | +12.5 ±24.5 |
| edit-data | heldout | 71 | 44.4 | 64.1 | +19.7 ±10.9 |
| edit-data | seen | 4 | 75.0 | 37.5 | -37.5 ±61.7 |
| read-code | heldout | 80 | 52.5 | 55.6 | +3.1 ±8.4 |
| read-code | seen | 4 | 75.0 | 75.0 | +0.0 ±0.0 |
| read-local | heldout | 71 | 66.9 | 69.0 | +2.1 ±12.5 |
| read-local | seen | 4 | 62.5 | 62.5 | +0.0 ±40.0 |
| search | heldout | 107 | 78.0 | 83.2 | +5.1 ±6.5 |
| stat | heldout | 71 | 44.4 | 47.2 | +2.8 ±10.2 |
| stat | seen | 4 | 50.0 | 75.0 | +25.0 ±49.0 |
| terminal | heldout | 60 | 17.5 | 11.7 | -5.8 ±6.2 |
| web-code | heldout | 100 | 28.0 | 30.0 | +2.0 ±7.6 |
| web-local | heldout | 129 | 59.3 | 63.2 | +3.9 ±6.0 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（120 次失败）：tests-failed 92%, no-required-tool 4%, answer-wrong 4%
- **code-fix** adapter（116 次失败）：tests-failed 91%, answer-wrong 6%, no-required-tool 3%
- **code-fix-oss** base（41 次失败）：tests-failed 100%
- **code-fix-oss** adapter（33 次失败）：tests-failed 100%
- **direct** base（43 次失败）：answer-wrong 51%, tools-when-none-needed 47%, used-forbidden-tool 2%
- **direct** adapter（35 次失败）：tools-when-none-needed 51%, answer-wrong 43%, no-required-tool 6%
- **edit-code** base（62 次失败）：answer-wrong 53%, file-result-wrong 31%, too-many-calls 10%, used-forbidden-tool 3%, no-required-tool 3%
- **edit-code** adapter（57 次失败）：answer-wrong 44%, file-result-wrong 42%, too-many-calls 11%, used-forbidden-tool 4%
- **edit-data** base（81 次失败）：file-result-wrong 64%, answer-wrong 31%, too-many-calls 5%
- **edit-data** adapter（56 次失败）：file-result-wrong 55%, answer-wrong 41%, too-many-calls 4%
- **read-code** base（78 次失败）：answer-wrong 64%, no-required-tool 28%, other 6%, wrote-in-read-only-turn 1%
- **read-code** adapter（73 次失败）：answer-wrong 56%, no-required-tool 34%, other 10%
- **read-local** base（50 次失败）：answer-wrong 96%, no-required-tool 4%
- **read-local** adapter（47 次失败）：answer-wrong 89%, no-required-tool 6%, used-forbidden-tool 4%
- **search** base（47 次失败）：no-web-search 60%, answer-wrong 28%, file-result-wrong 6%, too-many-calls 4%, wrote-in-read-only-turn 2%
- **search** adapter（36 次失败）：no-web-search 56%, answer-wrong 28%, file-result-wrong 14%, tests-failed 3%
- **stat** base（83 次失败）：answer-wrong 98%, tools-when-none-needed 2%
- **stat** adapter（77 次失败）：answer-wrong 97%, tools-when-none-needed 3%
- **terminal** base（99 次失败）：tests-failed 72%, file-result-wrong 27%, no-required-tool 1%
- **terminal** adapter（106 次失败）：tests-failed 69%, file-result-wrong 31%
- **web-code** base（144 次失败）：tests-failed 90%, no-web-fetch 5%, no-required-tool 4%, answer-wrong 1%
- **web-code** adapter（140 次失败）：tests-failed 85%, no-required-tool 7%, no-web-fetch 6%, wrote-in-read-only-turn 2%
- **web-local** base（105 次失败）：file-result-wrong 43%, answer-wrong 32%, tests-failed 9%, other 8%, no-required-tool 5%
- **web-local** adapter（95 次失败）：file-result-wrong 39%, answer-wrong 32%, no-required-tool 9%, tests-failed 9%, other 7%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 0% | 11.3 | 9% | 13% | - | - | - |
| code-fix | adapter | 0% | 10.9 | 8% | 11% | - | - | - |
| code-fix-oss | base | 0% | 5.0 | 7% | 7% | - | - | - |
| code-fix-oss | adapter | 0% | 4.2 | 7% | 5% | - | - | - |
| direct | base | 59% | 1.1 | 4% | 0% | - | - | - |
| direct | adapter | 59% | 1.2 | 0% | 0% | - | - | - |
| edit-code | base | 0% | 4.8 | 5% | 25% | - | - | - |
| edit-code | adapter | 0% | 5.1 | 5% | 22% | - | - | - |
| edit-data | base | 0% | 4.2 | 6% | 14% | - | - | - |
| edit-data | adapter | 0% | 4.1 | 2% | 10% | - | - | - |
| read-code | base | 0% | 5.0 | 4% | 2% | - | - | - |
| read-code | adapter | 0% | 5.7 | 4% | 2% | - | - | - |
| read-local | base | 2% | 2.4 | 1% | 1% | - | - | - |
| read-local | adapter | 1% | 3.1 | 2% | 1% | - | - | - |
| search | base | 3% | 2.5 | 11% | 1% | - | - | - |
| search | adapter | 2% | 2.7 | 11% | 1% | - | - | - |
| stat | base | 1% | 3.3 | 0% | 1% | - | - | - |
| stat | adapter | 1% | 3.5 | 2% | 1% | - | - | - |
| terminal | base | 0% | 10.7 | 4% | 6% | - | - | - |
| terminal | adapter | 0% | 10.2 | 5% | 7% | - | - | - |
| web-code | base | 0% | 11.1 | 9% | 11% | 100.0 | 5.0 | 0.06 |
| web-code | adapter | 0% | 10.0 | 10% | 10% | 99.0 | 10.5 | 0.1 |
| web-local | base | 0% | 5.5 | 8% | 10% | 98.8 | 5.8 | 0.0 |
| web-local | adapter | 0% | 5.7 | 9% | 10% | 99.2 | 10.1 | 0.01 |

## 变化最大的题（|差| ≥ 0.5，共 341 道；完整列表见 JSON）

- cfg-28051（直接回答-先答再查，heldout）：100.0 → 0.0；adapter 失败：{'no-required-tool': 2}
- cfg-28208（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'no-required-tool': 2}
- cfg-31054（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-31254（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-35039（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'used-forbidden-tool': 2}
- code-new-030（代码任务-Node，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- code-new-062（代码任务-Python-多模块，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- doc-33254（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-33261（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- doc-35158（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- fs-33714（统计计算-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33723（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-136（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-42（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-31173（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-31275（查找阅读-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-33377（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-34254（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35060（外部信息-网络加本地，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35218（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35223（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35232（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35241（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- live-a-156（外部信息-真实网页-Coding验收，heldout）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- log-34409（查找阅读-日志，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- …
- own-rc-019（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-022（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-025（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-051（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-rc-075（查找阅读-代码，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-004（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-023（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-076（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-096（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-107（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-se-110（外部信息-网络加本地，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-023（外部信息-真实网页-Coding验收，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-057（外部信息-真实网页-Coding验收，heldout）：0.0 → 100.0；adapter 失败：-
- own-wc-059（外部信息-真实网页-Coding验收，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-026（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-030（外部信息-真实网页-编程文档，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-074（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-20113（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-28056（直接回答-先答再查，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31042（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31108（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32025（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32206（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-34428（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- web-33076（外部信息-网络查询，heldout）：0.0 → 100.0；adapter 失败：-
