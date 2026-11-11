# 数据层面归因（自动生成）

- 基模：`runs/eval-v1-base-20261106T133528+runs/eval-v1-base-retry1+runs/eval-v1-base-retry2+runs/eval-v1fill-base-20261106T145050+runs/eval-new-v2-base-20261106T142051`
- adapter：`runs/eval-full-r16-261111-20261111T073415/2026-11-11__15-34-16`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 2.3 | 64.1 | +61.7 ±11.1 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 4.6 | 68.5 | +63.8 ±10.9 |
| 直接回答-知识直答 | 450 | 154 | 22 | 88.6 | 93.2 | +4.5 ±15.7 |
| 改文件写产物-代码 | 355 | 49 | 10 | 75.0 | 70.0 | -5.0 ±47.2 |
| 代码任务-Python | 317 | 29 | 46 | 22.8 | 76.1 | +53.3 ±14.4 |
| 代码任务-Node | 190 | 18 | 43 | 17.4 | 54.7 | +37.2 ±13.1 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 2.0 | 33.0 | +31.0 ±11.5 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 5.9 | 32.4 | +26.5 ±19.0 |
| 查找阅读-代码 | 116 | 22 | 84 | 39.9 | 55.4 | +15.5 ±10.8 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 4.8 | 57.1 | +52.4 ±20.8 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 40.8 | 61.5 | +20.8 ±13.4 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 8.3 | 66.7 | +58.3 ±23.6 |
| 直接回答-闲聊 | 81 | 22 | 13 | 80.8 | 96.2 | +15.4 ±17.1 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 45.7 | 72.9 | +27.1 ±16.7 |
| 改文件写产物-表格 | 72 | 10 | 9 | 16.7 | 55.6 | +38.9 ±27.2 |
| 统计计算-日志 | 71 | 10 | 22 | 15.9 | 43.2 | +27.3 ±15.4 |
| 外部信息-网络查询 | 69 | 10 | 86 | 76.2 | 90.7 | +14.5 ±8.7 |
| 统计计算-文件系统 | 69 | 10 | 8 | 37.5 | 68.8 | +31.2 ±41.2 |
| 查找阅读-日志 | 63 | 10 | 16 | 56.2 | 78.1 | +21.9 ±19.9 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 53.8 | 63.5 | +9.6 ±12.9 |
| 统计计算-表格 | 60 | 9 | 42 | 41.7 | 61.9 | +20.2 ±16.7 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 22.2 | 66.7 | +44.4 ±38.1 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 0.0 | 25.0 | +25.0 ±10.2 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 56.7 | 73.3 | +16.7 ±32.7 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 0.0 | 16.7 | +16.7 ±17.7 |
| 直接回答-做不到 | 25 | 7 | 17 | 50.0 | 47.1 | -2.9 ±28.5 |
| 改文件写产物-日志 | 5 | 1 | 2 | 100.0 | 50.0 | -50.0 ±98.0 |
| 统计计算-代码 | 5 | 2 | 2 | 75.0 | 50.0 | -25.0 ±147.0 |
| debugging | 0 | 0 | 40 | 37.5 | 56.2 | +18.8 ±16.3 |
| 直接回答-先答再查 | 0 | 0 | 23 | 41.3 | 76.1 | +34.8 ±24.2 |
| 终端操作-Shell | 0 | 0 | 60 | 0.0 | 14.2 | +14.2 ±7.8 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 37.5 | 56.2 | +18.8 ±16.3 |
| code-fix | heldout | 120 | 15.8 | 53.3 | +37.5 ±8.2 |
| code-fix | seen | 4 | 0.0 | 75.0 | +75.0 ±49.0 |
| direct | heldout | 71 | 63.4 | 76.8 | +13.4 ±12.0 |
| direct | seen | 4 | 75.0 | 100.0 | +25.0 ±49.0 |
| edit-code | heldout | 71 | 43.7 | 62.0 | +18.3 ±13.4 |
| edit-code | seen | 4 | 75.0 | 75.0 | +0.0 ±80.0 |
| edit-data | heldout | 71 | 43.0 | 64.1 | +21.1 ±11.6 |
| edit-data | seen | 4 | 50.0 | 37.5 | -12.5 ±61.7 |
| read-code | heldout | 80 | 41.9 | 54.4 | +12.5 ±10.7 |
| read-code | seen | 4 | 0.0 | 75.0 | +75.0 ±49.0 |
| read-local | heldout | 71 | 47.9 | 73.2 | +25.4 ±12.3 |
| read-local | seen | 4 | 37.5 | 75.0 | +37.5 ±46.9 |
| search | heldout | 107 | 62.1 | 84.1 | +22.0 ±8.6 |
| stat | heldout | 71 | 32.4 | 54.9 | +22.5 ±12.2 |
| stat | seen | 4 | 62.5 | 75.0 | +12.5 ±24.5 |
| terminal | heldout | 60 | 0.0 | 14.2 | +14.2 ±7.8 |
| web-code | heldout | 100 | 1.0 | 29.0 | +28.0 ±7.7 |
| web-local | heldout | 129 | 3.5 | 66.3 | +62.8 ±7.7 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（210 次失败）：tests-failed 59%, no-required-tool 39%, answer-wrong 1%, wrote-in-read-only-turn 0%, timeout 0%
- **code-fix** adapter（114 次失败）：tests-failed 87%, answer-wrong 8%, no-required-tool 5%
- **code-fix-oss** base（50 次失败）：tests-failed 100%
- **code-fix-oss** adapter（35 次失败）：tests-failed 100%
- **direct** base（54 次失败）：tools-when-none-needed 57%, answer-wrong 31%, no-required-tool 4%, used-forbidden-tool 4%, wrote-in-read-only-turn 4%
- **direct** adapter（33 次失败）：tools-when-none-needed 70%, answer-wrong 30%
- **edit-code** base（82 次失败）：answer-wrong 66%, file-result-wrong 32%, used-forbidden-tool 2%
- **edit-code** adapter（56 次失败）：file-result-wrong 46%, answer-wrong 43%, too-many-calls 7%, used-forbidden-tool 4%
- **edit-data** base（85 次失败）：file-result-wrong 55%, answer-wrong 42%, used-forbidden-tool 2%
- **edit-data** adapter（56 次失败）：file-result-wrong 68%, answer-wrong 29%, too-many-calls 4%
- **read-code** base（101 次失败）：answer-wrong 53%, no-required-tool 25%, wrote-in-read-only-turn 10%, other 10%, too-many-calls 2%
- **read-code** adapter（75 次失败）：answer-wrong 56%, no-required-tool 37%, other 7%
- **read-local** base（79 次失败）：answer-wrong 77%, no-required-tool 13%, used-forbidden-tool 6%, too-many-calls 3%, timeout 1%
- **read-local** adapter（40 次失败）：answer-wrong 95%, used-forbidden-tool 5%
- **search** base（81 次失败）：answer-wrong 42%, no-web-search 31%, file-result-wrong 12%, used-forbidden-tool 9%, wrote-in-read-only-turn 4%
- **search** adapter（34 次失败）：no-web-search 59%, answer-wrong 26%, file-result-wrong 12%, too-many-calls 3%
- **stat** base（99 次失败）：answer-wrong 90%, no-required-tool 6%, tools-when-none-needed 2%, timeout 2%
- **stat** adapter（66 次失败）：answer-wrong 100%
- **terminal** base（120 次失败）：tests-failed 57%, file-result-wrong 33%, no-required-tool 8%, answer-wrong 1%, timeout 1%
- **terminal** adapter（103 次失败）：tests-failed 71%, file-result-wrong 29%
- **web-code** base（198 次失败）：no-web-fetch 76%, tests-failed 16%, no-required-tool 7%, wrote-in-read-only-turn 1%
- **web-code** adapter（142 次失败）：tests-failed 80%, no-required-tool 13%, no-web-fetch 7%
- **web-local** base（249 次失败）：no-web-fetch 70%, no-required-tool 13%, answer-wrong 7%, file-result-wrong 6%, tests-failed 3%
- **web-local** adapter（87 次失败）：file-result-wrong 51%, answer-wrong 21%, other 10%, no-required-tool 8%, tests-failed 8%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 19% | 7.3 | 22% | 20% | - | - | - |
| code-fix | adapter | 0% | 10.5 | 8% | 10% | - | - | - |
| code-fix-oss | base | 8% | 2.8 | 8% | 1% | - | - | - |
| code-fix-oss | adapter | 0% | 4.0 | 5% | 5% | - | - | - |
| direct | base | 50% | 1.8 | 10% | 4% | - | - | - |
| direct | adapter | 59% | 1.4 | 0% | 0% | - | - | - |
| edit-code | base | 3% | 6.2 | 7% | 18% | - | - | - |
| edit-code | adapter | 0% | 5.0 | 5% | 22% | - | - | - |
| edit-data | base | 7% | 4.8 | 10% | 9% | - | - | - |
| edit-data | adapter | 0% | 4.1 | 4% | 12% | - | - | - |
| read-code | base | 10% | 7.0 | 12% | 14% | - | - | - |
| read-code | adapter | 0% | 5.6 | 2% | 2% | - | - | - |
| read-local | base | 1% | 4.9 | 8% | 5% | - | - | - |
| read-local | adapter | 0% | 2.9 | 1% | 1% | - | - | - |
| search | base | 4% | 3.7 | 14% | 3% | - | - | - |
| search | adapter | 2% | 2.7 | 8% | 1% | - | - | - |
| stat | base | 3% | 4.3 | 3% | 6% | - | - | - |
| stat | adapter | 2% | 3.5 | 1% | 0% | - | - | - |
| terminal | base | 6% | 7.3 | 4% | 4% | - | - | - |
| terminal | adapter | 0% | 11.2 | 5% | 8% | - | - | - |
| web-code | base | 39% | 3.1 | 22% | 9% | 27.0 | 7.5 | 0.18 |
| web-code | adapter | 0% | 9.9 | 10% | 9% | 100.0 | 13.0 | 0.12 |
| web-local | base | 28% | 3.7 | 42% | 14% | 34.9 | 36.4 | 0.12 |
| web-local | adapter | 0% | 5.8 | 6% | 11% | 100.0 | 7.8 | 0.01 |

## 变化最大的题（|差| ≥ 0.5，共 475 道；完整列表见 JSON）

- cfg-31049（改文件写产物-文档配置，seen）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- cfg-35349（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- code-25034（统计计算-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-33525（改文件写产物-代码，seen）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-35354（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- code-35357（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'too-many-calls': 2}
- doc-31412（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-31230（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33722（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-140（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-151（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-31169（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-31174（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35163（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35166（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- log-31106（改文件写产物-日志，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- nt-25280（直接回答-知识直答，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-dr-042（直接回答-做不到，heldout）：100.0 → 0.0；adapter 失败：{'tools-when-none-needed': 2}
- own-dr-043（直接回答-做不到，heldout）：100.0 → 0.0；adapter 失败：{'tools-when-none-needed': 2}
- own-dr-052（直接回答-先答再查，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-rc-030（查找阅读-代码，heldout）：100.0 → 0.0；adapter 失败：{'no-required-tool': 2}
- own-rc-051（查找阅读-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-rc-060（查找阅读-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-rc-086（查找阅读-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- own-se-014（外部信息-网络查询，heldout）：100.0 → 0.0；adapter 失败：{'no-web-search': 2}
- …
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
- own-wl-075（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-076（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-078（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-25006（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31029（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31108（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32014（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32015（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32025（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32029（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32202（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32212（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32307（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32315（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
