# Pi 后端：Pi + rwkv-pi

`backends/pi/harbor_agent.py` 里的 `PiRwkv` 把 [Pi](https://github.com/badlogic/pi-mono) 编程 agent 和 [rwkv-pi](../../../rwkv-pi) 接成 Harbor agent，和 `backends/dsh`（`DshRwkv`）遵守同一套框架接口（主 README “框架接口”），所以 `runner/` 读两边的结果完全一样。

```bash
PYTHONPATH=. harbor run -p tasks/<task> -a backends.pi.harbor_agent:PiRwkv \
  --ak rwkv_url=http://127.0.0.1:18411 --ak container_url=http://172.17.0.1:28411 -o runs
```

或者 `BACKEND=pi CONTAINER_URL=... scripts/eval-run.sh <rwkv_url> <tasks> <name>`（`calibrate.sh` 同理）。

## Pi 和 DSH 哪里不一样

| | DSH（`backends/dsh`） | Pi（`backends/pi`） |
|---|---|---|
| 框架 | DeepSeek Harness，npm 包 + profile 插件 | Pi 1.5.0，从 rwkv-pi 锁定的源码（`pi-source.lock.json`）直接跑 |
| RWKV 接入 | dsh-rwkv-plugin，profile 配置 | rwkv-pi 作为 Pi extension 注册 `rwkv` provider |
| 和引擎怎么说话 | 插件发请求（Lightning 或 irwkv） | rwkv-pi **自己把 Pi 的消息渲染成 RWKV 提示词**（`src/prompt.ts`），打 Lightning `/v1/batch/completions` 拿原始续写，客户端解析 XML 工具调用（`src/xml.ts`）；要求引擎在流里报告 `matched_stop` |
| 工具 | read/edit/write/bash/grep/glob/web 等 | 训练白名单 `read,write,edit,bash`（`--tools`），**没有 grep 和 web 工具** |
| 网页题 | `web.json` 存档由回放插件喂给 web 工具 | 没有 web 工具，存档用不上；`turns.json` 里记 `web_archive_ignored: true`，不悄悄算分 |
| 多轮 | 每轮一个 `headless.ts` 进程 | 每轮一个 Pi 进程，第 2 轮起 `--continue` 续同一个 session |
| 事件流 | DSH 原生写 `events.jsonl` | Pi 写 session JSONL，`turn.mjs` 转成同一套事件（session / text / reasoning / tool_call / tool_result / status / final） |
| 请求追踪 | 插件自带 | `trace.mjs`：只监听 undici 的 `diagnostics_channel`，记下每次引擎请求/响应原文，不记 Authorization |
| 步数上限 | 插件参数 | `budget.mjs`：数 `turn_end`，到数就 abort，**不改提示词**（Harbor 自带的 Pi `max_turns` 会往系统提示词里加一句话，训练里没有） |
| 引擎位置 | 容器里跑，引擎要能从容器访问 | 同左：Pi 在任务容器里跑，`container_url` 必须是容器能到的地址 |

和训练一致（rwkv-pi 生成训练数据时的设置）：

- 启动参数照抄 rwkv-pi `src/cli.ts`：`--no-extensions --extension dist/extension.js --provider rwkv --thinking high --tools read,write,edit,bash --no-skills --no-context-files --no-prompt-templates`，加 `RWKV_PI_PARITY=1`。
- Pi 设置照抄 rwkv-pi `harness.ts`：关闭 compaction，关闭重试（`maxRetries 0`）。
- 系统提示词只含 cwd，不含日期、模型名，所以不需要 DSH 那样的 persona / 时区开关。
- `RWKV_CONTEXT_WINDOW` 默认取模型 id 里的 `ctxNNNNN`（G1L 7.2B 是 34304），rwkv-pi 从不截断输入，超了就报错。

## 引擎要求

rwkv-pi 只信任**锁定版本的 Lightning**（`lightning-source.lock.json`，`d54c536`）：它在流结束时要看到 `matched_stop`，否则拒绝执行工具（“Lightning stopped without a configured text boundary; tool execution refused.”）。旧版 Lightning 能回话但不报这个字段，Pi 后端在上面会一个工具都调不出来，`diagnose.py` 里表现为 `engine_error`。跑之前确认端点是锁定版本。

引擎只绑 127.0.0.1 又不方便重启时，用 `scripts/engine-bridge.py 172.17.0.1:<端口> 127.0.0.1:<引擎端口>` 在 docker 网桥上开一个转发口，`container_url` 填它。`install()` 会在容器里先请求一次 `/v1/models`，到不了直接失败，不会跑出一堆假 0 分。

## 工具链

不在容器里联网安装。`backends/pi/build-toolchain.sh [rwkv-pi 目录]` 打出 `.cache/rae-pi-<label>-linux-<arch>.tar.gz`（约 83 MB，解到 `/opt/rae-pi`）：Node、Pi 源码、从 rwkv-pi HEAD 编译的 `dist/`、`node_modules`、本目录的三个 `.mjs`。label 是 `rwkv-pi-<短 commit>`，源码有未提交改动时加 `-dirty` 并把 diff 写进清单。**`.env*` 永远不打包**（rwkv-pi 在里面放引擎和 teacher 的 key）。

高并发时 `scripts/prepare-toolchain.sh pi` 在宿主机解压一次、只读挂载；`scripts/sync-server.sh` 加 `BACKEND=pi` 会把 rwkv-pi 的已跟踪文件（含 `.git`，不含 `.env`）和工具链包一起同步过去。

## 每个 trial 留下什么

除了框架接口要求的 `final.txt`、`events.jsonl`、`turns.json`、`events-N.jsonl`、`final-N.txt`、`session-N.txt`、`ws-N.json`：

- `pi-N.txt`：Pi `--mode json` 的输出流（去掉逐 token 的 `message_update`），`pi.txt` 是各轮拼起来的。
- `pi/sessions/*.jsonl`：Pi 原生 session，Harbor 据此生成 ATIF `trajectory.json` 和 token 统计。
- `trace/NNNN.{request.json,response.txt,meta.json}`：每次引擎请求。
- `provenance.json`：端点 `/v1/models` 原文、工具链 sha256 和构建清单、rwkv-pi 和本仓库的 HEAD + 未提交 diff、所有 RWKV_* 设置。
- `version()`：`pi <版本>; rwkv-pi <commit>; toolchain <label>; eval <commit>; model ...; backend ...; adapter ...; tools ...; thinking ...; harbor ...`。

## 失败模式（`runner/diagnose.py` 的标签）

G1L 7.2B 在 TBLite 2.0 的 1/5 子集上跑 Pi 后端（2026-11-12）看到的，和 terminus-2 的“大多超时”完全不同：Pi 后端的运行几乎都在几分钟内被 rwkv-pi 主动结束。

| 标签 | 含义 | 来源 |
|---|---|---|
| `loop_guard` | 同一个失败调用连续 3 次，rwkv-pi 的 `RWKV_TOOL_LOOP` 结束本轮（交互场景里等用户补充指令；单轮评测里就是结束） | rwkv-pi loop guard |
| `max_tokens` | 一次回复写满 `RWKV_MAX_TOKENS`（8192），通常是思考块里打转 | 模型 |
| `unknown_tool` | 调用了白名单外的工具（`execute_bash`、`execute_code`、`run_shell`），返回 `Tool X not found` | 模型 |
| `truncated_call` | 工具调用没闭合，rwkv-pi 拒绝执行 | rwkv-pi XML 解析 |
| `unclosed_think` | 回复停在思考块里 | rwkv-pi XML 解析 |
| `context_overflow` | 提示词超过上下文（rwkv-pi 不截断），Pi 报成 “Connection error.” | trace 里最后一次 `/tokens/count` |
| `engine_error` | 其他 provider 错误，比如引擎不报 `matched_stop` | — |

注意：rwkv-pi 拒绝的回复（`truncated_call` 等）不报 usage，这一步的 token 数记为 0，所以 Pi 后端的输出 token 统计偏低；看实际生成量以 `trace/` 为准。

Harbor 的 agent 超时直接杀掉进程时，`turn.mjs` 来不及跑；`populate_context_post_run` 会在宿主机上用 Pi 的 session 日志补出 `events.jsonl`、`final.txt`，`turns.json` 标 `recovered_after_kill`（Python 版转换和 `turn.mjs` 由 `test/test_convert.py` 保证一致）。

## 测试

```bash
node --test backends/pi/test/*.test.mjs
PYTHONPATH=. python3 -m pytest backends/pi/test/test_convert.py
```

`tasks/env-pi-probe` 是 Pi 版的环境探针（用 bash 找文件），`eval-run.sh` / `calibrate.sh` 在 `BACKEND=pi` 时先跑它。
