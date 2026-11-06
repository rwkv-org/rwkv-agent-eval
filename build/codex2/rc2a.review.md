# rc2a 审查报告

范围：own-rc-051～own-rc-070，共 20 题、26 轮。先完整阅读 SPEC.md 和 rc2a.prompt，再逐题阅读全部 files、独立推导答案并与 reference 和 bank/judge.py 的实际行为核对。全部为只读代码题，没有网页/搜索题、网页存档、受保护程序检查或参考修复。

| id | 结论 | 原因 |
| --- | --- | --- |
| own-rc-051 | 已修 | defer 调用且内部执行 RemoveAll 的函数确为 DiscardWorkspace；修正查看工具替代判据。 |
| own-rc-052 | 已修 | 配置链输出依次为 137、83 秒，daytime 文件并未被加载；修正工具判据及数值子串匹配。 |
| own-rc-053 | 已修 | 工作流经 release-bundle、bundle.sh 最终调用 verify_bundle_manifest；修正查看工具替代判据。 |
| own-rc-054 | 已修 | errors.New 在 internal/slots/check.go 创建错误，HTTP 层只是转发；修正查看工具替代判据。 |
| own-rc-055 | 已修 | 独立展开得到 12−2−2+1=9 组，其中 arm64 为 3 组；修正工具判据及“十九”命中“九”等漏洞。 |
| own-rc-056 | 已修 | check_uppercase_rejected 检查 valid_unit_label 的返回值，现有测试确实拒绝大写；修正查看工具替代判据。 |
| own-rc-057 | 已修 | Linux 构建标签选择 diskWriter，Put 定义在 internal/writer/disk.go；修正查看工具替代判据。 |
| own-rc-058 | 已修 | 读取 PID 并发送 USR1 的函数是 request_log_reopen；修正查看工具替代判据。 |
| own-rc-059 | 已修 | Compose 解析分别得到端口 7589、7527；消除题面“启动服务”与只读要求的冲突，并修正工具及数值匹配。 |
| own-rc-060 | 已修 | Await 的停止回调经 StopHook 闭包调用 Worker.FlushAndClose；修正查看工具替代判据。 |
| own-rc-061 | 已修 | managed 且有客户端时返回 46，external 分支提前返回 0；修正工具判据及数值子串匹配。 |
| own-rc-062 | 已修 | 两条 .PHONY 声明去重后是 bundle、clean、inspect、publish、verify，共 5 个；修正工具及数值匹配。 |
| own-rc-063 | 已修 | above_ceiling 子用例以 101 调用 CheckHumidity 并检查错误，现有 Go 测试通过；修正查看工具替代判据。 |
| own-rc-064 | 已修 | 工作流引用现行 composite action，guarded 分派到 scripts/lanes/checked.sh；修正查看工具替代判据。 |
| own-rc-065 | 已修 | EqualSignedBody 直接使用 hmac.Equal，SignBody 只负责计算签名；修正查看工具替代判据。 |
| own-rc-066 | 已修 | override 得到 guarded，立即展开得到 guarded-releases-east，来源为 config/guard.mk；修正查看工具替代判据。 |
| own-rc-067 | 已修 | audit_nodes 经函数名回调最终调用 probe_tls_endpoint；只读追踪无需安装 openssl，修正查看工具替代判据。 |
| own-rc-068 | 已修 | workflow 版本 2.8.4 与标签 v2.8.5 不匹配，输出 VERSION_REF_MISMATCH 并返回 78；修正查看工具替代判据。 |
| own-rc-069 | 已修 | Names(false) 接受 status/inspect/st/sync/pull/doctor 六个字符串，主命令三个；修正工具及数值匹配。 |
| own-rc-070 | 已修 | 带空格根目录的测试直接调用 backup_object_path，现有测试验证完整输出路径；修正查看工具替代判据。 |

验证：每题修改后分别执行 `python3 bank/check_own.py bank/own/cases/<id>.json`，最后仅对本批 20 个文件集中执行，20/20 通过；在断网的 Debian `python:3.12-slim` 容器中再次执行同一批自检，也是 20/20 通过。

另在本机和上述容器验证全部 26 轮均接受 read/grep/glob/bash 任一种查看工具，拒绝无工具、空答、write/edit 写操作及被改动的文件快照；遍历数值等价答案，并检查错误数字不通过。两端均通过所有 Shell 文件的语法检查、052 的两条配置链、056/070 的现有测试、061 的两个状态分支、064 的 guarded 分派、068 的匹配/不匹配分支，以及 067 的回调链（用 Shell 函数替代 openssl，仅记录参数，不联网）。

本机另外用 Compose config 验证 059 的两个端口，用 GNU Make 验证 066 的覆盖和展开，用 GOOS=linux 的 go list 验证 057 的构建文件选择；七个 Go 项目均通过 go test ./...，其中只有 063 原本含 Go 测试，其余主要验证编译。Debian 镜像没有 Go、Make 或 openssl，不声称在该镜像内执行过这些工具；题面均要求只读推导，回答不依赖这些工具存在。没有执行 Docker 构建、部署或实际服务操作。

结论数量：OK 0，已修 20，已删 0，有风险 0。保留 20 题；简单 7、中等 9、困难 4；中文 12、英文 8；两轮题 6。

最常见问题：20 题均将 required_tools 写成 read，而当前 judge.py 只对旧查看工具名称或 bash 启用查看类互换，导致只用 grep/glob/bash 的正确解被误杀；本批统一使用 required_tools: ["bash"]，实际接受四种查看工具，并不强制使用 bash。其次是 6 题、11 轮的数字别名使用子串匹配，中文“九”会接受“十九”，也会将包含正确数字的错误复合回答判对；这些原本要求只答数值的轮次改用 output_equals_any，保留中英文、全角、常见小数/补零/千分位及单位写法，并允许常见计数前缀。没有增加 output_excludes、expected_number 的 40 字符限制或工具调用次数限制。059 另消除了只读题面中的命令式启动要求。
