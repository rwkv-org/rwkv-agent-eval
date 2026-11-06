# rwkv-agent-eval

RWKV 模型 Agent 能力的考卷：给 RWKV 一个真实的任务和一套工具，看它能不能自己把事做完。

考两种角色：

- **主 Agent**：独立推进一个任务，比如修 bug、改配置、跑测试。
- **子 Agent**：替主 Agent 做的窄任务，比如在仓库里找代码、查资料。

模型要通过一个 Agent 框架（harness）才能用工具，所以分数衡量的是“模型 + 框架”这个组合。目前接入的框架是 [dsh-rwkv-plugin](https://github.com/No-22-Github/dsh-rwkv-plugin)，也就是以 RWKV 为模型的 DeepSeek Harness；以后可以在 `backends/` 下接入别的框架（比如 Pi）。每次运行都会记下模型 checkpoint、插件版本和 DSH 版本，用来比较不同权重、adapter 或框架改动的效果。

考卷由两部分组成：自有题和挑选过的开源题，都是 [Harbor](https://docs.harborframework.com) 的 task 目录格式，全部用 Harbor + Docker 跑。题目、框架、环境三者分开：题目不知道谁来答、在哪跑；框架是 `backends/` 下的 Harbor agent；环境由 `harbor run` 选。

## 目录

```
tasks/<name>/            自有题，Harbor 格式（task.toml、instruction.md、environment/、tests/、solution/）
datasets.lock.toml       开源题：Harbor 注册表的 dataset@version + 选中的 task ID
backends/dsh/            DSH + dsh-rwkv-plugin 的 Harbor agent（harbor_agent.py）和工具链打包脚本
runner/report.py         多次运行逐题对比
runner/diagnose.py       一次运行的失败模式统计（读 DSH 事件流）
runs/                    Harbor job 目录（不入库）
.cache/                  工具链包等（不入库）
```

## 自有题的约定

就是标准 Harbor 题，另加几条约定：

- `task.toml` 的 `[metadata]` 写：
  - `role = "main" | "sub"`：主 Agent 独立推进任务（写代码、部署），还是子 Agent 的窄任务（探索仓库、查资料、整理报告）
  - `difficulty`、`source`、`category`
  - 看终答判分的题加 `answer = true`
- 初始文件放 `environment/workspace/`，`environment/Dockerfile` 用 `COPY workspace/ /app/`，工作目录是 `/app`。
- `tests/test.sh` 把奖励写到 `/logs/verifier/reward.txt`。
- 看终答的题读 `/logs/agent/final.txt`（见下面的框架接口），**不要**在题面里要求“把答案写进某个文件”：子 Agent 实际是直接回话、由框架转给主 Agent，题面要和实战一致。
- 每道题都要有 `solution/solve.sh`；改题后先用 oracle 校验：`harbor run -p tasks/<name> -a oracle`。终答题的 solve.sh 自己写 `/logs/agent/final.txt`。

## 框架接口

`backends/<name>/` 下的每个 Harbor agent 都要做到：

- 跑完后把 agent 的**最后一条回复**原样写到 `/logs/agent/final.txt`（没有回复就写空文件）。终答题只读这个文件，所以漏了这一步，终答题会全部 0 分，看起来却像模型答错。
- `version()` 返回 `dsh <版本>; plugin <commit>; eval <commit>` 这种 `key value; ...` 格式，`report.py` 从这里读框架版本（commit 带 `*` 表示有未提交改动）。

## 跑法

先构建一次工具链包（Node + DSH + pnpm，以后每题上传，不在容器里联网安装）：

```bash
backends/dsh/build-toolchain.sh 0.2.1-rc.5
```

跑自有题（`-p tasks` 跑整个目录，`-p tasks/<name>` 跑一题，`-k 3` 每题跑 3 次）：

```bash
PYTHONPATH=. harbor run -p tasks -a backends.dsh.harbor_agent:DshRwkv --ak rwkv_url=http://host:8000 -k 3 -o runs
```

插件默认取同级目录的 `../dsh-rwkv-plugin`，可用 `--ak plugin_dir=...` 指定。模型 id 和后端类型（lightning / irwkv）从端点的 `/v1/models` 自动读；端点同时挂了多个模型时才需要 `--ak rwkv_model=...`，手动传的值和端点对不上会直接报错。

对比两次运行、看失败模式：

```bash
python3 runner/report.py runs/<A> runs/<B>
```

```bash
python3 runner/diagnose.py runs/<A> --list
```

## 每次运行记下什么

全自动，不用手填：

- 每个 trial 的 `result.json`：agent 的 `version()`，含 `dsh`、`plugin`、`eval` 的 commit（带 `*` 表示有未提交改动）、端点实际报告的 `model`、`backend`、`adapter`、`harbor` 版本；还有题目内容哈希（`task_checksum`），`report.py` 据此区分“题改了”和“模型变了”。
- 每个 trial 的 `agent/provenance.json`：端点 `/v1/models` 原始回复、工具链包 sha256、插件和本仓库的完整 HEAD、**未提交的 diff 和未跟踪文件列表**（`*` 的版本也能复原）、宿主平台。
- job 目录的 `config.json`：命令行参数（端点等）。

同一配置两次运行的逐题结果会大量翻转（试点里 30 题两次通过的几乎不重叠），比较版本时每题至少跑 3 次。
