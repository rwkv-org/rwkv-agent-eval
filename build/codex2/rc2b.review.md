# rc2b 审查报告

已完整阅读 `bank/own/SPEC.md`、`build/codex2/rc2b.prompt`、`bank/judge.py` 和 `bank/check_own.py`，逐题阅读 own-rc-071 至 own-rc-090 的全部 files，独立推导后与参考答案及判据比较。20 题原参考答案均与源码一致。

下表中的“工具等价”修复指：将每轮 `required_tools: ["read"]` 改为 `["bash"]`。当前 judge 仅对旧查看类名称及 bash 应用查看工具互相替代逻辑，`["read"]` 实际会误杀只用 bash、grep 或 glob 的正确解；`["bash"]` 可接受 read/bash/grep/glob 四种工具，符合本批规范，不代表强制执行 shell。

| id | 结论 | 原因及处理 |
| --- | --- | --- |
| own-rc-071 | 已修 | DOM 事件绑定最终调用 `commitLayerDrop`，答案正确；修复工具等价误杀。 |
| own-rc-072 | 已修 | 原首轮答案 `adjusted_total` 已在题面参数中直接给出；改问 CSV 首条 value，独立计算为 207，去掉 CLI 覆盖后的追问为 210，并修复工具等价、补齐数字写法。 |
| own-rc-073 | 已修 | `submitBasket → placePantryOrder → postKitchenTicket`，末者直接执行 POST；修复工具等价误杀。 |
| own-rc-074 | 已修 | `reject_repeated_span` 直接抛错，追问的第三个身份字段为 `district`；两轮依赖成立，修复工具等价误杀。 |
| own-rc-075 | 已修 | bulk 关闭时方法/路径数为 2+3+2+1=8，中间件不计；修复工具等价并补充小数及科学计数写法。 |
| own-rc-076 | 已修 | 指定 JUnit 用例直接断言 `freeDeskCount`，并非 `reservableDeskCount`；修复工具等价误杀。 |
| own-rc-077 | 已修 | browser 条件实际进入 `src/stores/session-store.ts`；去除仅文件名/路径尾部的宽松候选，避免 `src/retired/session-store.ts` 也通过，并修复工具等价。 |
| own-rc-078 | 已修 | `split_unmapped_regions` 将 Elmford 行分流到 quarantine；修复工具等价误杀。 |
| own-rc-079 | 已修 | public 被映射到 cold，目标策略将等待值覆盖为 1320 ms，移除该覆盖后为环境值 2600 ms；补充三位小数、科学计数及秒/毫秒写法，修复工具等价。 |
| own-rc-080 | 已修 | recording 分支经包装器进入 `emitBatchFrame`，其 partition 来自 `context.upload_id`；两轮答案正确，修复工具等价误杀。 |
| own-rc-081 | 已修 | `require_segment_seal` 对不存在或空封签直接构造 MissingSeal，再映射为协议错误码；修复工具等价误杀。 |
| own-rc-082 | 已修 | 递归去重后的作业为 extract/scrub/geo/totals/manifest/publish，共 6 个；修复工具等价并补充数值写法。 |
| own-rc-083 | 已修 | 指定 Node 测试直接调用 `flushPendingSignals`，现有测试确实检查只写一次；修复工具等价误杀。 |
| own-rc-084 | 已修 | 命令入口经 signed provider 别名进入 `wheelmanifest/formats/signed_list.py`，schema 为 `wheel-manifest/v3`；明确相对项目根路径、去除尾部候选以拒绝 `legacy/signed_list.py`，修复工具等价。 |
| own-rc-085 | 已修 | `nextEnabledIndex` 执行索引循环和 disabled 跳过，前后方向及环回行为一致；修复工具等价误杀。 |
| own-rc-086 | 已修 | JVM tokenize 覆盖环境 redact 和默认 HASH，外发字符串为 `vault-token`；修复工具等价误杀。 |
| own-rc-087 | 已修 | 生成器链最终由 `encode_latency_row` 直接调用 writerow，导出 18/26 ms；修复工具等价误杀。 |
| own-rc-088 | 已修 | 远端失败后缓存年龄为 36000 ms，大于 30000 ms，映射得到 `THUMBNAIL_SOURCE_STALE`；修复工具等价误杀。 |
| own-rc-089 | 已修 | 屏幕集合共 8 项，其中 workspace 子树 4 项，禁用 billing 子树与布局/重定向均不计；修复工具等价并补充数值写法。 |
| own-rc-090 | 已修 | 指定 unittest 直接调用并断言 `aggregate_hour_samples`，末桶保留行为与结果一致；修复工具等价误杀。 |

验证结果：

- 每道题修改后立即单独运行 `python3 bank/check_own.py bank/own/cases/<id>.json`，20/20 通过；最后在只读挂载仓库的 `python:3.12-slim` Debian 容器中，对本批 20 个文件再运行一次批量自检，20/20 通过。
- 26 轮均验证 read/bash/grep/glob 可替代；无工具调用、write/edit 调用以及任一受保护文件内容变化均判失败；另外 30 个正确/错误答案探针全部符合预期，包含长数值回复、单位变体及错误目录。
- 7 个 Python 项目的相关流程在本机与 `python:3.12-slim` 中复核；7 个 TypeScript 项目使用本机可用的 TypeScript 6.0.3 在临时目录编译，编译输出及另外 3 个 JavaScript 项目在本机 Node 与 `node:24-bookworm` Debian 容器中复核；083 的两项 Node 测试、090 的两项 unittest 均通过。
- 两个 Java 项目以 `javac --release 17` 编译并运行关键方法断言；Rust 项目以 edition 2021 编译并验证缺少封签、空封签、正常发布及空段分支。这三题只读求解不依赖评测容器安装 Java/Rust；未运行 Maven/JUnit 套件。
- 本批全部为只读代码题，无网页/搜索题、web-archive 存档、终端脚本修复或 `expect.checks` 受保护执行测试；网页答案位置、搜索 match、参考修复及 BSD/GNU 脚本差异不适用。所有原始项目 files 与整题文件保护判据均保留。
- 6 道两轮题的追问均继续使用前轮定位或配置/集合，没有拼接无关问题；修复后答案均需读取项目特有源码或数据，不属于常识。没有 `output_excludes` 的旧值误伤，也没有 `expected_number` 默认 40 字限制。

规则判分的共同边界：contains 类判据仍只证明回复提到了正确标识符/数字，无法理解否定句或排除“枚举全部候选”的回答；查看工具要求也只能证明调用，无法证明读取了相关内容。此为现有 judge 的通用限制，本次未修改批次外判分器，也未以格式严苛的全文相等判据替代自然语言事实判据。

汇总：OK 0；已修 20；已删 0；有风险 0；共 20 题。最常见的问题是全部 20 题、26 轮均存在的查看工具替代误杀；其次为路径尾部匹配过宽（2 题）、数值等价写法不足（4 道原数值题），以及题面直接给出答案（1 题）。批次保留 7 easy / 9 medium / 4 hard，中文 12 / 英文 8，单轮 14 / 双轮 6。
