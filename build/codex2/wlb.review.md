已完整阅读 `bank/own/SPEC.md`、`build/codex2/wlb.prompt`，逐题阅读全部本地文件，通过 `web_tool.py show/fetch --grep` 核对全部存档，并独立推导答案。20 道均保留；参考答案和参考修改均正确，无需补抓网页。所有存档均为 200，所需规则在正文 @369–@11527，未超过约 15000。本批没有搜索题，搜索词匹配检查不适用；全部单轮，无跨轮依赖问题。构成为中文 12 / 英文 8、简单 10 / 中等 8 / 较难 2、只读 10 / 修改 10。

全批共同修复：`judge.py` 对 `required_tools: ["read"]` 实际严格匹配，使用 bash/grep 查看文件也会误判。改为 `["web_fetch", "bash"]`，利用判分器已有的查看类工具替代规则，实测 read/grep/glob/bash 均可通过，参考仍使用 read。网页调用要求保留。

10 道只读题原先仅检查答案子串，同时列出所有候选也能通过，数字题甚至接受负数。保留原有答案存在性检查，增加判分器已支持的 `output_equals_any`，按题面“只答一个标识/数值”的要求确认完整答案，同时接纳引号、Markdown、代码块、中英文简短答案标签、全角和合理数字写法；未引入 `output_excludes` 或数值回复长度限制。

| id | 结论 | 一句话原因 |
|---|---|---|
| own-wl-021 | 已修 | @11527 规定无单位超时为毫秒，4700ms 小于 5s，答案 catalog-summary-28 正确；修复工具误杀及枚举候选可过判。 |
| own-wl-022 | 已修 | @11436 明确 ON_ERROR_STOP 下脚本 SQL 错误退出码为 3，参考仅改目标数字正确；修复工具误杀。 |
| own-wl-023 | 已修 | @2561 的 verify-full 同时校验证书链和主机名，生效服务为 ledger-stream；修复工具误杀及枚举服务可过判。 |
| own-wl-024 | 已修 | @3656 的迁移最后一步要求 scram-sha-256，参考仅修改 report_reader 行且保留 loader 正确；修复工具误杀。 |
| own-wl-025 | 已修 | @369 定义匹配时返回零，对应 contact-coral-46，ASCII 大小写规则也吻合；修复工具误杀及枚举记录可过判。 |
| own-wl-026 | 已修 | @2228 规定 SQLITE_OPEN_READONLY 只读且缺文件报错，参考保留 URI 标志正确；修复工具误杀。 |
| own-wl-027 | 已修 | @7484 规定此前字符数加一，冷柜前有六字符，独立 SQLite 查询得到 7；修复工具误杀、-7 可过判及答案格式覆盖。 |
| own-wl-028 | 已修 | @383 明确只读/读写/不存在分别为 1/0/-1，参考三处修正均正确；修复工具误杀。 |
| own-wl-029 | 已修 | @4333–@4387 区分 Redis 2.8 之后的 -2/-1，答案 warehouse:route:coral-38 正确；修复工具误杀及枚举 key 可过判。 |
| own-wl-030 | 已修 | @8511 明确 KEEPTTL 保留已有 TTL，参考只追加该选项且适用于本地 Redis 7.2；修复工具误杀。 |
| own-wl-031 | 已修 | @4733、@5121 规定 -2 为倒数第二项且 stop 包含端点，答案 pick-ash-51 正确；修复工具误杀及枚举元素可过判。 |
| own-wl-032 | 已修 | @7283 的 EXPIRE NX 只在无过期时间时设置，参考仅修改目标 key 的行正确；修复工具误杀。 |
| own-wl-033 | 已修 | @456 的 empty_gif 直接生成透明单像素 GIF，对应 /metrics/pulse-73.gif；修复工具误杀及错误前缀路径可过判。 |
| own-wl-034 | 已修 | @1090、@3405 支持 charset utf-8 及仅显式列 application/json；修复工具误杀，并改用可信完整内容检查接纳等效大小写和参数引号。 |
| own-wl-035 | 已修 | @604 规定镜像响应被忽略，当前请求主上游为 202；修复工具误杀、-202 可过判，并接受 202 Accepted 等状态写法。 |
| own-wl-036 | 已修 | @1293–@1655 区分 json/jsonp，参考仅将客户端选中的 /incoming/ 改为 json 正确；修复工具误杀。 |
| own-wl-037 | 已修 | @2555 规定 get 返回首个参数值，独立 JavaScript 执行得到 spring-coral-72；修复工具误杀及同时列出两值可过判。 |
| own-wl-038 | 已修 | @10953 要求 SameSite=None 配套 Secure；修复工具误杀、网络请求禁令与打开文档的冲突，并允许属性名的等效大小写。 |
| own-wl-039 | 已修 | @2620 规定空字符串不触发 ?? 回退，独立追踪及 JavaScript 执行均得到 canal-route-86；修复工具误杀及枚举路由可过判。 |
| own-wl-040 | 已修 | @2502 说明 toSorted 返回排序副本，参考只改调用链上的方法名，执行前后验证排序结果相同且修复后原数组保持 81,14,53；修复工具误杀。 |

第 034/038 题新增的检查代码位于可信 `expect.checks` 的 `python3 -c` 参数中，需求文档列入 `protected_files`，同时保留文档不变判据；没有把答案或测试脚本加进模型可见的本地 files。检查完整文件，只放宽目标参数的等效拼写，仍拒绝缺属性、错误 MIME/字符集、重复属性、改端口、改 SameSite、删除 HttpOnly 等错误。大小写等价依据 [RFC 9110 §8.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.3)、[RFC 6265 §5.2.5](https://www.rfc-editor.org/rfc/rfc6265.html#section-5.2.5)，并核对了 [nginx MIME 类型处理源码](https://raw.githubusercontent.com/nginx/nginx/master/src/http/ngx_http.c) 和 [charset 模块源码](https://raw.githubusercontent.com/nginx/nginx/master/src/http/modules/ngx_http_charset_filter_module.c)。

每次修改后均对该题运行 `python3 bank/check_own.py bank/own/cases/<id>.json`；最终整批 macOS 与断网 Debian `python:3.12-slim` 自检均为 20/20。两种环境的同一组额外判分验证结果一致：20 份参考通过、20 份完全不操作失败、80 组查看工具替代通过、688 组正确答案写法通过、50 组错误答案被拒绝、10 份只调用工具但不改文件的修改题失败、19 组等效配置写法通过、28 组错误文件修改及 13 组旁支文件篡改被拒绝，另分别验证 20 组缺网页工具和 20 组缺本地查看工具均失败。

本批没有需实际执行的 Shell 脚本修复题，也无原有受保护测试；SQL/C/Redis/nginx/JavaScript 文件主要用于静态阅读或精确修改，题面禁止执行的服务命令无需容器提供。新增检查仅依赖 Python 标准库，已在 Debian 实跑，无 BSD/GNU 命令差异或 git/jq/curl/gawk 依赖。JavaScript 行为另在本机 Node 验证，未声称在 Debian 容器安装或运行 Node，亦未启动 PostgreSQL、Redis 或 nginx 服务。

仍存在判分器共有边界：required_tools 只记录工具名称，不能证明打开了指定 URL 或查看了全部必要文件；例如 glob 被算作查看类工具。这是现有判分器的能力限制，不能在本批题目文件内彻底消除。本批保留本地特有标识/配置、正确完整答案及文件终态检查，单凭题面常识或完全不操作无法通过；未修改判分器。

汇总：OK 0，已修 20，已删 0，有风险 0（无须单独挂起的题目；上述判分器共有边界已披露）。仅修改本批 20 个 cases 文件及本报告，20 份网页存档、本地输入文件和参考修复内容均保持不变，未执行 git commit。最常见问题是严格要求 read 导致合理工具替代被误杀（20 题），其次是只检查答案是否出现导致枚举候选和错误数字/路径可混过（10 题），另有等效大小写/引号误杀（2 题）及题面网络禁令冲突（1 题）。
