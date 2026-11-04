# rwkv-agent-eval

RWKV Agent 的评测题库与跑分工具。题目统一用 [Harbor](https://docs.harborframework.com) 的 task 目录格式，按“需不需要一个可以随便改坏的隔离环境”分两类跑：

| `environment` | 什么题 | 怎么跑 |
|---|---|---|
| `workspace` | 轻量题：改个 CSS、查一下时间、读几个文件回答问题 | `runner/workspace.py`，不起容器，靠 DSH 自己的 workspace-write 沙箱 |
| `docker` | 重题：多轮修改、装依赖、部署项目；开源题库 | Harbor + Docker，agent 用 `backends/dsh/harbor_agent.py` |

## 目录

```
tasks/<name>/            自有题，Harbor 格式（task.toml、instruction.md、environment/、tests/、solution/）
datasets.lock.toml       开源题：Harbor 注册表的 dataset@version + 选中的 task ID
backends/dsh/            DSH + dsh-rwkv-plugin：workspace.py（workspace runner 用）、harbor_agent.py（Harbor 用）
runner/workspace.py      跑 workspace 题
runner/report.py         多次运行逐题对比
runs/                    运行记录（不入库）
.cache/                  工具链包等（不入库）
```

## 自有题的约定

在 Harbor 格式之上只多几条约定，题目照样能被 Harbor 直接跑：

- `task.toml` 的 `[metadata]` 写：
  - `environment = "workspace" | "docker"`
  - `role = "main" | "sub"`：主 Agent 独立推进任务，还是子 Agent 的窄任务（探索仓库、查资料）
  - `difficulty`、`source`、`category`
  - 看终答判分的题加 `answer = true`
- workspace 题的初始文件放 `environment/workspace/`；`environment/Dockerfile` 只做 `COPY workspace/ /app/`，这样同一道题也能用 Harbor 跑。
- `tests/test.sh` 用 `${RAE_TESTS_DIR:-/tests}`、`${RAE_LOGS_DIR:-/logs}` 定位文件，奖励写到 `$LOGS/verifier/reward.txt`。Harbor 里两个变量为空，走默认路径；workspace runner 会把它们指向本机目录。
- workspace runner 把时区设成 UTC，和 Docker 镜像默认一致。
- 看终答的题读 `$LOGS/agent/final.txt`。两个后端都会把 agent 的最后一条消息写到这里。
- 每道题都要有 `solution/solve.sh`；改题后先跑 oracle 校验：`python3 runner/workspace.py --oracle`。

## 跑法

workspace 题：

```bash
python3 runner/workspace.py --backend dsh --opt base_url=http://host:8000 --opt model=rwkv7-g1l-7.2b --opt dsh_root=../deepseek-harness
```

不填 `dsh_root` 时用 PATH 里的 `dsh`（npm 版 `@deepseek-ai/dsh`）。插件默认取同级目录的 `../dsh-rwkv-plugin`。

docker 题（先构建一次工具链包，以后每题上传，不在容器里联网安装）：

```bash
backends/dsh/build-toolchain.sh 0.2.1-rc.5
```

```bash
PYTHONPATH=. harbor run -p tasks/css-button-dark -a backends.dsh.harbor_agent:DshRwkv --ak rwkv_url=http://host:8000 --ak rwkv_model=rwkv7-g1l-7.2b
```

对比两次运行：

```bash
python3 runner/report.py runs/<A> runs/<B>
```

## 每次运行记下什么

`runs/<name>/run.json`：模型与端点（checkpoint、adapter）、插件 commit（带 `*` 表示有未提交改动）、DSH 版本、本仓库 commit；`results.jsonl` 每题另记题目内容哈希，`report.py` 据此区分“题改了”和“模型变了”。

同一配置两次运行的逐题结果会大量翻转（试点里 30 题两次通过的几乎不重叠），比较版本时每题至少跑 3 次。
