# 数据层面归因（自动生成）

- 基模：`runs/eval-v1-base-20261106T133528+runs/eval-v1-base-retry1+runs/eval-v1-base-retry2+runs/eval-v1fill-base-20261106T145050+runs/eval-new-v2-base-20261106T142051`
- adapter：`runs/eval-v1-nora-r16-20261106T121434+runs/eval-v1-nora-r16-retry1+runs/eval-v1-nora-r16-retry2+runs/eval-v1fill-nora-r16-20261106T151737+runs/eval-new-v2-nora-r16-20261106T142306`
- 题数：1019（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%

## 按训练领域

| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |
|---|--:|--:|--:|--:|--:|--:|
| 外部信息-真实网页-编程文档 | 1119 | 95 | 64 | 2.3 | 60.2 | +57.8 ±11.2 |
| 外部信息-真实网页-系统与数据 | 662 | 71 | 65 | 4.6 | 59.2 | +54.6 ±10.7 |
| 直接回答-知识直答 | 450 | 154 | 22 | 88.6 | 90.9 | +2.3 ±18.8 |
| 改文件写产物-代码 | 355 | 49 | 10 | 75.0 | 85.0 | +10.0 ±38.1 |
| 代码任务-Python | 317 | 29 | 46 | 22.8 | 65.2 | +42.4 ±13.3 |
| 代码任务-Node | 190 | 18 | 43 | 17.4 | 57.0 | +39.5 ±15.8 |
| 外部信息-真实网页-Coding验收 | 171 | 13 | 50 | 2.0 | 25.0 | +23.0 ±9.4 |
| 代码任务-Python-多模块 | 130 | 7 | 17 | 5.9 | 35.3 | +29.4 ±20.7 |
| 查找阅读-代码 | 116 | 22 | 84 | 39.9 | 48.8 | +8.9 ±11.2 |
| 外部信息-网络加本地 | 109 | 10 | 21 | 4.8 | 40.5 | +35.7 ±20.4 |
| 改文件写产物-跨类混合 | 85 | 10 | 65 | 40.8 | 54.6 | +13.8 ±14.8 |
| 改文件写产物-文件系统 | 81 | 10 | 12 | 8.3 | 37.5 | +29.2 ±28.2 |
| 直接回答-闲聊 | 81 | 22 | 13 | 80.8 | 76.9 | -3.8 ±30.3 |
| 查找阅读-文档配置 | 80 | 10 | 35 | 45.7 | 74.3 | +28.6 ±22.5 |
| 改文件写产物-表格 | 72 | 10 | 9 | 16.7 | 55.6 | +38.9 ±35.7 |
| 统计计算-日志 | 71 | 10 | 22 | 15.9 | 20.5 | +4.5 ±11.0 |
| 外部信息-网络查询 | 69 | 10 | 86 | 76.2 | 88.4 | +12.2 ±9.2 |
| 统计计算-文件系统 | 69 | 10 | 8 | 37.5 | 75.0 | +37.5 ±48.1 |
| 查找阅读-日志 | 63 | 10 | 16 | 56.2 | 59.4 | +3.1 ±27.5 |
| 改文件写产物-文档配置 | 62 | 10 | 52 | 53.8 | 55.8 | +1.9 ±14.0 |
| 统计计算-表格 | 60 | 9 | 42 | 41.7 | 57.1 | +15.5 ±18.1 |
| 查找阅读-跨类混合 | 56 | 10 | 9 | 22.2 | 44.4 | +22.2 ±36.9 |
| 统计计算-跨类混合 | 52 | 9 | 1 | 0.0 | 0.0 | +0.0 |
| 外部信息-真实网页-Coding混合 | 48 | 5 | 50 | 0.0 | 25.0 | +25.0 ±9.8 |
| 查找阅读-文件系统 | 42 | 10 | 15 | 56.7 | 73.3 | +16.7 ±32.7 |
| 代码任务-Node-多模块 | 32 | 2 | 18 | 0.0 | 19.4 | +19.4 ±16.1 |
| 直接回答-做不到 | 25 | 7 | 17 | 50.0 | 35.3 | -14.7 ±21.9 |
| 改文件写产物-日志 | 5 | 1 | 2 | 100.0 | 50.0 | -50.0 ±98.0 |
| 统计计算-代码 | 5 | 2 | 2 | 75.0 | 0.0 | -75.0 ±49.0 |
| debugging | 0 | 0 | 40 | 37.5 | 50.0 | +12.5 ±18.8 |
| 直接回答-先答再查 | 0 | 0 | 23 | 41.3 | 69.6 | +28.3 ±25.3 |
| 终端操作-Shell | 0 | 0 | 60 | 0.0 | 10.8 | +10.8 ±6.6 |

## 按能力块 × 是否训练过

| 能力块 | split | 题数 | 基模 | adapter | 差值 |
|---|---|--:|--:|--:|--:|
| code-fix-oss | oss | 40 | 37.5 | 50.0 | +12.5 ±18.8 |
| code-fix | heldout | 120 | 15.8 | 50.4 | +34.6 ±8.3 |
| code-fix | seen | 4 | 0.0 | 87.5 | +87.5 ±24.5 |
| direct | heldout | 71 | 63.4 | 69.0 | +5.6 ±13.0 |
| direct | seen | 4 | 75.0 | 75.0 | +0.0 ±0.0 |
| edit-code | heldout | 71 | 43.7 | 57.0 | +13.4 ±14.2 |
| edit-code | seen | 4 | 75.0 | 87.5 | +12.5 ±61.7 |
| edit-data | heldout | 71 | 43.0 | 50.7 | +7.7 ±12.2 |
| edit-data | seen | 4 | 50.0 | 87.5 | +37.5 ±73.5 |
| read-code | heldout | 80 | 41.9 | 47.5 | +5.6 ±11.0 |
| read-code | seen | 4 | 0.0 | 75.0 | +75.0 ±49.0 |
| read-local | heldout | 71 | 47.9 | 68.3 | +20.4 ±14.8 |
| read-local | seen | 4 | 37.5 | 50.0 | +12.5 ±61.7 |
| search | heldout | 107 | 62.1 | 79.0 | +16.8 ±8.5 |
| stat | heldout | 71 | 32.4 | 46.5 | +14.1 ±12.8 |
| stat | seen | 4 | 62.5 | 37.5 | -25.0 ±28.3 |
| terminal | heldout | 60 | 0.0 | 10.8 | +10.8 ±6.6 |
| web-code | heldout | 100 | 1.0 | 25.0 | +24.0 ±6.7 |
| web-local | heldout | 129 | 3.5 | 59.7 | +56.2 ±7.7 |

## 失败类型（占失败 trial 的比例）

- **code-fix** base（210 次失败）：tests-failed 59%, no-required-tool 39%, answer-wrong 1%, wrote-in-read-only-turn 0%, timeout 0%
- **code-fix** adapter（120 次失败）：tests-failed 78%, timeout 14%, answer-wrong 6%, no-required-tool 2%, wrote-in-read-only-turn 1%
- **code-fix-oss** base（50 次失败）：tests-failed 100%
- **code-fix-oss** adapter（40 次失败）：tests-failed 95%, timeout 5%
- **direct** base（54 次失败）：tools-when-none-needed 57%, answer-wrong 31%, no-required-tool 4%, used-forbidden-tool 4%, wrote-in-read-only-turn 4%
- **direct** adapter（46 次失败）：answer-wrong 54%, tools-when-none-needed 41%, used-forbidden-tool 4%
- **edit-code** base（82 次失败）：answer-wrong 66%, file-result-wrong 32%, used-forbidden-tool 2%
- **edit-code** adapter（62 次失败）：answer-wrong 61%, file-result-wrong 31%, used-forbidden-tool 3%, too-many-calls 3%, timeout 2%
- **edit-data** base（85 次失败）：file-result-wrong 55%, answer-wrong 42%, used-forbidden-tool 2%
- **edit-data** adapter（71 次失败）：file-result-wrong 56%, answer-wrong 44%
- **read-code** base（101 次失败）：answer-wrong 53%, no-required-tool 25%, wrote-in-read-only-turn 10%, other 10%, too-many-calls 2%
- **read-code** adapter（86 次失败）：answer-wrong 58%, no-required-tool 34%, other 7%, wrote-in-read-only-turn 1%
- **read-local** base（79 次失败）：answer-wrong 77%, no-required-tool 13%, used-forbidden-tool 6%, too-many-calls 3%, timeout 1%
- **read-local** adapter（49 次失败）：answer-wrong 94%, no-required-tool 4%, used-forbidden-tool 2%
- **search** base（81 次失败）：answer-wrong 42%, no-web-search 31%, file-result-wrong 12%, used-forbidden-tool 9%, wrote-in-read-only-turn 4%
- **search** adapter（45 次失败）：no-web-search 69%, answer-wrong 27%, file-result-wrong 4%
- **stat** base（99 次失败）：answer-wrong 90%, no-required-tool 6%, tools-when-none-needed 2%, timeout 2%
- **stat** adapter（81 次失败）：answer-wrong 74%, timeout 23%, tools-when-none-needed 2%
- **terminal** base（120 次失败）：tests-failed 57%, file-result-wrong 33%, no-required-tool 8%, answer-wrong 1%, timeout 1%
- **terminal** adapter（107 次失败）：tests-failed 56%, file-result-wrong 30%, timeout 13%, answer-wrong 1%
- **web-code** base（198 次失败）：no-web-fetch 76%, tests-failed 16%, no-required-tool 7%, wrote-in-read-only-turn 1%
- **web-code** adapter（151 次失败）：tests-failed 63%, timeout 17%, no-web-fetch 9%, wrote-in-read-only-turn 7%, no-required-tool 4%
- **web-local** base（249 次失败）：no-web-fetch 70%, no-required-tool 13%, answer-wrong 7%, file-result-wrong 6%, tests-failed 3%
- **web-local** adapter（104 次失败）：file-result-wrong 47%, answer-wrong 25%, no-required-tool 9%, tests-failed 8%, other 6%

## 行为特征

| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| code-fix | base | 19% | 7.3 | 22% | 20% | - | - | - |
| code-fix | adapter | 0% | 9.9 | 8% | 7% | - | - | - |
| code-fix-oss | base | 8% | 2.8 | 8% | 1% | - | - | - |
| code-fix-oss | adapter | 0% | 4.3 | 7% | 0% | - | - | - |
| direct | base | 50% | 1.8 | 10% | 4% | - | - | - |
| direct | adapter | 58% | 1.3 | 4% | 0% | - | - | - |
| edit-code | base | 3% | 6.2 | 7% | 18% | - | - | - |
| edit-code | adapter | 0% | 4.5 | 6% | 16% | - | - | - |
| edit-data | base | 7% | 4.8 | 10% | 9% | - | - | - |
| edit-data | adapter | 0% | 3.8 | 7% | 6% | - | - | - |
| read-code | base | 10% | 7.0 | 12% | 14% | - | - | - |
| read-code | adapter | 0% | 4.9 | 4% | 2% | - | - | - |
| read-local | base | 1% | 4.9 | 8% | 5% | - | - | - |
| read-local | adapter | 2% | 2.5 | 1% | 2% | - | - | - |
| search | base | 4% | 3.7 | 14% | 3% | - | - | - |
| search | adapter | 3% | 2.5 | 9% | 0% | - | - | - |
| stat | base | 3% | 4.3 | 3% | 6% | - | - | - |
| stat | adapter | 1% | 3.2 | 0% | 1% | - | - | - |
| terminal | base | 6% | 7.3 | 4% | 4% | - | - | - |
| terminal | adapter | 0% | 9.7 | 5% | 2% | - | - | - |
| web-code | base | 39% | 3.1 | 22% | 9% | 27.0 | 7.5 | 0.18 |
| web-code | adapter | 0% | 9.5 | 10% | 5% | 99.0 | 5.5 | 0.03 |
| web-local | base | 28% | 3.7 | 42% | 14% | 34.9 | 36.4 | 0.12 |
| web-local | adapter | 0% | 5.3 | 10% | 4% | 98.8 | 6.6 | 0.01 |

## 变化最大的题（|差| ≥ 0.5，共 472 道；完整列表见 JSON）

- cfg-20135（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- cfg-27130（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-31070（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-31256（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- cfg-35306（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-25034（统计计算-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- code-31074（改文件写产物-代码，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-27380（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- doc-31148（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 1, 'answer-wrong': 1}
- doc-31152（改文件写产物-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- doc-31379（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-31412（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- doc-33268（查找阅读-文档配置，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-31230（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- fs-33722（查找阅读-文件系统，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- humanevalfix__python-131（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-151（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-25（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-65（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- humanevalfix__python-71（debugging，oss）：100.0 → 0.0；adapter 失败：{'tests-failed': 2}
- hyb-31169（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-31174（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-33663（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'answer-wrong': 2}
- hyb-35163（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- hyb-35166（改文件写产物-跨类混合，heldout）：100.0 → 0.0；adapter 失败：{'file-result-wrong': 2}
- …
- own-wl-057（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-059（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-063（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-066（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-067（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-068（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-069（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-071（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-072（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-075（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-078（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- own-wl-080（外部信息-真实网页-系统与数据，heldout）：0.0 → 100.0；adapter 失败：-
- tab-25006（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31029（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31118（改文件写产物-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-31140（改文件写产物-表格，seen）：0.0 → 100.0；adapter 失败：-
- tab-31406（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32014（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32015（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32029（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32207（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32212（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32236（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32314（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
- tab-32315（统计计算-表格，heldout）：0.0 → 100.0；adapter 失败：-
