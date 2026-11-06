# own-rc-001～own-rc-050 审查报告

本次只审查，不修改或删除题目、判分器及其它仓库文件，不提交 git；本报告为唯一交付文件。按“只审不改”的处理要求使用 OK / 应修 / 应删 / 有风险，不使用表示已经动过题目的“已修/已删”。

已完整阅读 `bank/own/SPEC.md`、`build/codex/rc.prompt` 和 `bank/judge.py`，逐题读取全部 files、全部轮次、参考回复和判据，独立推导全部 74 轮答案。下表中多个答案按轮次排列，均与现有参考答案一致。50 题全部属于只读的“查找阅读-代码”，没有网页/搜索题、网页存档依赖、参考修复或受保护的修复测试，因此网页位置、搜索词命中及参考补丁最小性不适用。

共同问题代码（下表引用）：

- **R1：查看工具替代被误杀，50 题 / 74 轮。** 全部轮次要求 `required_tools: ["read"]`，而 `bank/judge.py:32` 的 `OLD_DISCOVERY` 不含 `read`，第 120 行的替代分支只对旧工具名或 `bash` 生效。正确回答配合 `bash` 读文件、或配合 `grep` 查看相关内容，仍报 `required tool read not called`，与规范约定的查看类工具互换不符。完整回放中，50 题把参考查看工具换成 `bash` 后均失败。修订时应修正这一共同判分逻辑，或使用当前实现确实支持互换的判据；本次均未改动。
- **R2：只读约束漏检新增文件，50 题。** 每轮 `unchanged_files` 和整题 `expect.files` 都完整覆盖初始文件，且会拦截 write/edit；但 `bash` 新建其它文件不在检查范围内。逐题完整回放：保留参考答案及初始文件，只增加一次 bash 调用和 `unexpected.txt`，50/50 仍通过。这违背全部题面“不要修改或生成文件”的要求。应补充新增文件检查。
- **R3：数值匹配同时误杀和放水，18 题 / 28 轮。** 全部 28 个数值轮的正确全角写法都失败；27 个非零数值轮在答案前加负号都仍通过，例如 `-7300`、`-4`、`-137`、`-2.6`。汉字不被 `contains_token` 当作词字符，导致“四十”通过答案“四”的检查，“十九”通过答案“九”的检查。`7300ms`、`37s` 等紧连英文单位的等价数值也没有兼容。应按数值及单位规范化后比较，并保留对中文数字的支持。
- **R4：名称/路径只验证局部命中。** 下划线不属于判分器的词字符，第 1 题的错误名称 `not_stable_photo_key` 会通过；路径允许裸文件名，又只做局部匹配，第 12 题的不存在路径 `does-not-exist/rules.py`、第 24 题的 `src/handlers/obsolete/signed.ts` 也会通过。单列裸文件名属于合理兼容，但不应让明确给错目录的完整路径也通过。第 47 题还有真实存在的错误包路径误命中，见下表。

## 逐题结论

| id | 结论 | 一句话原因 |
|---|---|---|
| own-rc-001 | 应修 | `src/names.py` 的 `stable_photo_key` 执行规范化、casefold 和空白连接，答案正确，存在 R1/R2 及错误名称 `not_stable_photo_key` 通过的 R4。 |
| own-rc-002 | 应修 | boot 显式覆盖得到 `7300`、撤去覆盖后取环境值 `6200`，两轮答案正确，存在 R1/R2/R3，且正确的 `7300ms` 被拒绝。 |
| own-rc-003 | 应修 | main → relay.Deliver → sink.AppendAudit 的末端函数为 `AppendAudit`，答案唯一，存在 R1/R2。 |
| own-rc-004 | 应修 | `guard_window` 对保留天数 2 发出告警，`return $?` 向上传递 `47`，答案正确且 Debian 实跑一致，存在 R1/R2/R3。 |
| own-rc-005 | 应修 | 关闭管理路由为 `4`、开启为 `6`、其中 POST 为 `2`，三轮依赖明确，存在 R1/R2/R3，错误答案“四十”可通过第一轮。 |
| own-rc-006 | 应修 | `accepts_short_fraction` 直接断言 `readAmount(' 18,7 ') == 1870`，并非 formatAmount，答案正确，存在 R1/R2。 |
| own-rc-007 | 应修 | import 方向为 collector → policy，答案 `collector` 正确，存在 R1/R2，且题面给出两候选包导致不读代码有二选一猜中风险。 |
| own-rc-008 | 应修 | source 加载 `lib/remote.sh`，有效配置使 PUT 的 bucket 为 `pg-archive-eu3`，答案及 Debian 输出正确，存在 R1/R2。 |
| own-rc-009 | 应修 | `unique_addresses` 以 strip/casefold 后的值保序去重，prepare 使用该函数，答案正确，存在 R1/R2。 |
| own-rc-010 | 应修 | 空值合并保留 CLI 的 `0`，依次撤去 CLI/profile 后为 `7`、`19`，三轮答案正确，存在 R1/R2/R3。 |
| own-rc-011 | 应修 | refresh_mirror → mirror_manifest → `checksum_index` 最终调用 sha256sum，答案正确，Debian 提供该命令且本题无需执行摘要，存在 R1/R2。 |
| own-rc-012 | 应修 | TICKET_REUSED 的实际 raise 点为 `src/rules.py`，不是异常类文件，答案正确，存在 R1/R2 及不存在路径也通过的 R4。 |
| own-rc-013 | 应修 | MAP_CACHE=off 得到 `3` 个命令、改为 on 得到 `5` 个，run 字段不增加命令数，存在 R1/R2/R3。 |
| own-rc-014 | 应修 | TestPaddedGrid 直接调用 `ParseGridRef` 并断言拆分结果，答案唯一，存在 R1/R2。 |
| own-rc-015 | 应修 | CHANNEL_HELPER 解析为 `lib/channels/edge.sh`，未加载 stable 脚本中的反向 source 不影响当前链，答案正确，存在 R1/R2。 |
| own-rc-016 | 应修 | 注册表绑定 `seasonal_demand`，定义文件为 `src/reports/current.py`，旧 annual_demand 未使用，两轮答案正确，存在 R1/R2。 |
| own-rc-017 | 应修 | `collectHandles` 用正则提取 handle、转小写并经 Set 去重，hasBroadcast 不承担该行为，答案正确，存在 R1/R2。 |
| own-rc-018 | 应修 | 正数 override 优先得到 `37`、override=0 时取 `83`、环境解析失败回退 `61`，三轮答案正确，存在 R1/R2/R3。 |
| own-rc-019 | 应修 | CODEC=zstd 使 compact_shard 选择 `pack_zstd`，答案正确且静态阅读可得，Debian 缺 zstd 不改变所问的分派函数，存在 R1/R2。 |
| own-rc-020 | 应修 | store_reading 先验证 age_seconds，901 先触发 `READING_STALE`，负 watts 的验证不可达，答案正确，存在 R1/R2。 |
| own-rc-021 | 应修 | Enabled(false) 过滤两个夜间任务得到 `3`、true 得到 `5`，答案正确，存在 R1/R2/R3。 |
| own-rc-022 | 应修 | check_slug_spaces 直接调用 `profile_slug` 并比较 north-gate，库及测试在 Debian 实跑通过，存在 R1/R2。 |
| own-rc-023 | 应修 | `src/notify.py` 导入 templates 中的 hold_message，方向及答案正确，存在 R1/R2，题面两候选文件也带来二选一猜中风险。 |
| own-rc-024 | 应修 | barrel 将 receiveSigned 重导出为 acceptWebhook，实际文件 `src/handlers/signed.ts`、auth 为 `signed-v2`，存在 R1/R2 及错误完整路径命中的 R4。 |
| own-rc-025 | 应修 | Resolve 优先使用 contracted 的 rail 绑定，因此实际计价函数为 `TieredRailRate`，FlatRailRate 是干扰项，存在 R1/R2。 |
| own-rc-026 | 应修 | shell 按缺省→site→CLI 顺序覆盖得到 `97`，答案及 Debian 输出正确，存在 R1/R2/R3，且题面已给 `--keep 97`，可按常见 CLI 语义猜中。 |
| own-rc-027 | 应修 | export_visit → encode_visit → `journal_record`，key 源字段为 `visit_id`、stream 为 `visits-west-4`，三轮答案正确且相关，存在 R1/R2。 |
| own-rc-028 | 应修 | 若将 badge 序列化后传给 scan 则为 `BADGE_REVOKED`，但题面未明确传入 JSON 字符串，直接传对象会先触发 JSON.parse 错误，另有 R1/R2。 |
| own-rc-029 | 应修 | Router(false) 只注册 `4` 个 method/path pattern，debug 分支不注册，答案正确，存在 R1/R2/R3，错误“四十”仍通过。 |
| own-rc-030 | 应修 | CI source 的有效库直接测试 `retry_delay`，传入 attempt 为 `9` 而非输出 28，Debian 两个 CI 脚本通过，存在 R1/R2/R3，错误“十九”通过第二轮。 |
| own-rc-031 | 应修 | `src/publish.ts` 直接导入 codec，反方向没有 import，答案正确，存在 R1/R2，题面两候选文件有二选一猜中风险。 |
| own-rc-032 | 应修 | live 是 aggregate 的导入别名，实际 SumOutput 定义在 `internal/aggregate/sum.go`，previous/peak.go 未导入，答案正确，存在 R1/R2。 |
| own-rc-033 | 应修 | `strip_host_comments` 用 sed 删除注释和空行，HOST_COMMENT 来自 `conf/names.env`，Debian 清洗输出一致，存在 R1/R2。 |
| own-rc-034 | 应修 | 默认 11→TOML 17→环境 31→调用覆盖 `24`，最终 poll_seconds 正确，存在 R1/R2/R3。 |
| own-rc-035 | 应修 | display 分支经闭包及导入别名最终调用定义名 `presentCents`，并非 formatPassengerFare 或 encodeCents，答案正确，存在 R1/R2。 |
| own-rc-036 | 应修 | `CheckPressure` 直接产生错误，严格阈值为 `137`，输入阈值本身时 Accept 返回 `PRESSURE_OK`，三轮答案正确，存在 R1/R2/R3。 |
| own-rc-037 | 应修 | issue/renew/revoke/inspect/help 共 `5` 个命名分支，通配错误分支不计，答案唯一，存在 R1/R2/R3。 |
| own-rc-038 | 应修 | 指定断言直接调用 `summarize_day`，classify_pm25 仅被其间接调用，测试期望与实现一致，存在 R1/R2。 |
| own-rc-039 | 应修 | board 只从 `src/domain.ts` 导入类型、随后确认 `src/view.ts` 导入该类型，两轮答案正确且相关，题面明确要求源路径故 `.js` 导入说明符不等价，存在 R1/R2。 |
| own-rc-040 | 应修 | init 将 shop 注册表项从 text 替换为 html，实际文件为 `internal/html/receipt.go`，答案正确，存在 R1/R2。 |
| own-rc-041 | 应修 | `choose_accessible_seat` 先过滤 step_free 再按 distance_to_ramp 取最小，区别于普通编号分配，答案正确，存在 R1/R2。 |
| own-rc-042 | 应修 | tunnel 的 73 被上限夹为 `53`，显式 options.heartbeat=0 优先后被下限夹为 `11`，两轮答案正确，存在 R1/R2/R3。 |
| own-rc-043 | 应修 | Tomorrow 的末端计算函数为 stock 包的 `AvailableLoaves`，ReservedLoaves 未在链上，答案正确，存在 R1/R2。 |
| own-rc-044 | 应修 | 有效配置阈值 89 且比较为 -ge，最小告警百分比为 `89`，Debian 验证 88 成功、89 告警返回 73，存在 R1/R2/R3。 |
| own-rc-045 | 应修 | CORE 3 项加 WRITABLE 2 项再加插件净增 2 项，覆盖 /health 后共 `7` 个不同键，答案正确，存在 R1/R2/R3。 |
| own-rc-046 | 应修 | rejects_short_load 直接调用 `acceptManifest(6,8)`，内部 manifestStatus 得到 `short`，两轮答案正确且状态标识符无需翻译，存在 R1/R2。 |
| own-rc-047 | 应修 | 真实方向为 cache → feed，答案 `cache` 正确，但错误答案 `ferry-weather-cache/internal/feed` 因项目名含 cache 也整题通过，另有 R1/R2。 |
| own-rc-048 | 应修 | common 先加载、CHANNEL=canary 后加载并替换同名函数，有效定义为 `lib/channels/canary.sh`，答案及 Debian 输出正确，存在 R1/R2。 |
| own-rc-049 | 应修 | 定价函数 `tag_price` 使用 `TAG_STEP`，Decimal('2.04')×1.25=2.55 按 0.1 半入得到 `2.6`，三轮答案正确，存在 R1/R2/R3。 |
| own-rc-050 | 应修 | patch 中显式 undefined 经对象展开覆盖 profile/env，最终空值回退至默认 `16`，答案正确，存在 R1/R2/R3。 |

## 汇总与验证

| 结论 | 数量 |
|---|---:|
| OK | 0 |
| 应修 | 50 |
| 应删 | 0 |
| 有风险 | 0 |
| 合计 | 50 |

50 道“应修”来自可复现的共同判分问题；独立核对未发现参考答案错误或必须删除的题。表内附带的猜中风险不另计一道“有风险”。没有改题，因此已修/已删均为 0。

最常见问题为 **R1 查看工具替代误杀（50 题）** 和 **R2 只读约束漏检新增文件（50 题）**，其次为 **R3 数值匹配不完整（18 题 / 28 轮）**；另需关注 R4 的局部名称/路径误匹配。028 应明确将 badge 作为 JSON 字符串传入 scan；其参考值是在该自然意图下推导的。二选一依赖方向题（007、023、031、047）及直接提供 CLI 数值的 026 有额外猜中风险，适合提高答案对仓库内容的依赖。007 与 047、023 与 031 等题也存在相近依赖方向考点重复；这是批次覆盖质量风险，无需据此删除已跑分题。

- 本机运行针对这 50 个文件的 `python3 bank/check_own.py <50 个路径>`：**50/50 通过**；Debian 的 `python:3.12-slim`（Python 3.12.16）中再次运行同一批自检：**50/50 通过**。自检只回放参考答案及空白答案，不能排除本报告的误杀/放水问题。
- 对全部 50 题做 `check_own.replay` 完整判分回放：正确答案只用 bash 查看时 **50/50 被拒**；保留初始文件而额外生成文本文件时 **50/50 被接受**；正确数值改为全角时 **28/28 轮被拒**；27 个非零正确数值取负数时 **27/27 轮被接受**。
- 50/50 空白回复、无工具的空操作均不能通过；只读题本身无需修改文件是预期行为。18 道多轮题都围绕前轮定位的函数、配置或结果继续追问，未发现无关问题硬拼。
- Debian 禁网、仓库只读挂载，临时项目全部在系统临时目录：实际核验全部 13 道 Python 题的关键调用/结果；对 Shell 题 004、008、015、022、026、030、033、037、044、048 做运行验证，其中 030 两个 CI 脚本、044 阈值两侧均通过；检查未依赖 git/jq/curl/gawk 或 BSD 特有选项。
- 其余 Shell 011 的 sha256sum 在 Debian 可用；019 仅问选择的函数，答案无需执行 zstd。12 道 Go 题和 13 道 TypeScript 题已逐文件静态追踪，不声称在缺 Go/Node 的 Debian 镜像中编译运行。这批全是只读分析题，没有要求模型安装这些运行时，判分也不执行题内 Go/TS 测试。
- 全部轮次均无 `output_excludes`、`expected_number`、`max_output_chars`，不存在旧值提及被排除或 expected_number 默认 40 字符限制的问题；函数名、标识符按题面需要保留代码拼写，裸文件名/相对路径/绝对路径均已有兼容，但仍需解决 R4。
- 批次结构符合数量配比：中文题面 30、英文 20；easy 15、medium 25、hard 10；单轮 32、两轮 12、三轮 6；每题 6～9 个文件。题面中的 `.env` 作为 env 统一按其键值映射理解，所有推导与此一致。

题目、存档、判分器及出题要求均未修改，也未 git commit。
