# rwkv-agent-eval

RWKV 模型 Agent 能力的考卷：给 RWKV 一个真实的任务和一套工具，看它能不能自己把事做完。

考两种角色：

- **主 Agent**：独立推进一个任务，比如修 bug、改配置、跑测试。
- **子 Agent**：替主 Agent 做的窄任务，比如在仓库里找代码、查资料。

模型要通过一个 Agent 框架（harness）才能用工具，所以分数衡量的是“模型 + 框架”这个组合。目前接入两个框架：[dsh-rwkv-plugin](https://github.com/No-22-Github/dsh-rwkv-plugin)（以 RWKV 为模型的 DeepSeek Harness，`backends/dsh`）和 rwkv-pi（以 RWKV 为模型的 Pi 编程 agent，`backends/pi`，两者差异见 [backends/pi/README.md](backends/pi/README.md)）。每次运行都会记下模型 checkpoint、框架及其 RWKV 接入的版本，用来比较不同权重、adapter 或框架改动的效果。

考卷由两部分组成：自有题和挑选过的开源题，都是 [Harbor](https://docs.harborframework.com) 的 task 目录格式，全部用 Harbor + Docker 跑。题目、框架、环境三者分开：题目不知道谁来答、在哪跑；框架是 `backends/` 下的 Harbor agent；环境由 `harbor run` 选。

## 目录

```
tasks/<name>/            自有题，Harbor 格式（task.toml、instruction.md、environment/、tests/、solution/）
datasets.lock.toml       开源题：Harbor 注册表的 dataset@version + 选中的 task ID
bank/                    从训练题库转来的题和自造题（见下面“题库”）
  convert.py             题库 case JSON → Harbor 题（build/candidates/），打能力块/split 标签
  judge.py               判分（管线 judge.ts 的移植），validate_judge.py 用 teacher 轨迹核对
  own/                   自造题：SPEC.md 规范，cases/*.json，check_own.py 自检
  web-archive/           真实网页题的页面存档（capture_pages.py 生成），评测时回放
  calib_report.py        校准结果按能力块汇总
backends/dsh/            DSH + dsh-rwkv-plugin 的 Harbor agent（harbor_agent.py）、网页回放插件（web-replay.mjs）、工具链脚本
backends/pi/             Pi + rwkv-pi 的 Harbor agent（harbor_agent.py）、事件转换/追踪/步数上限（turn.mjs、trace.mjs、budget.mjs）、工具链脚本
scripts/                 sync-server.sh（同步到跑分服务器）、prepare-toolchain.sh、calibrate.sh、eval-run.sh、backend.sh（BACKEND=dsh|pi）、engine-bridge.py
runner/report.py         多次运行逐题对比
runner/diagnose.py       一次运行的失败模式统计（读事件流，两个框架同一格式）
runs/                    Harbor job 目录（不入库）
build/                   生成的题目目录（不入库，可由 convert.py 重建）
.cache/                  工具链包、数据集等（不入库）
```

## 题库

训练数据（rwkv-agent-pipeline 的 mix-20261106）是 teacher 在管线题库上跑出来的。题库分三块：

- **留出题**：管线题库里没进训练的 case（`convert.py --pool heldout`），带 `split = "heldout"`；
- **已训回测**：从训练用过的 case 里每块抽 4 题（`split = "seen"`），用来区分“没学会”和“学会了但泛化不了”；
- **自造题**：训练题库用光了的能力块（查找阅读·代码、直接回答、代码修复）用 Codex 按 `bank/own/SPEC.md` 造，每题必须过 `check_own.py`（参考答案判过、什么都不做判挂、题面不和训练题重复）。

每题的 `[metadata]` 有 `block`（评测能力块）、`category`（训练数据的领域名，可回查训练行）、`split`、`origin_case`、`teacher`（teacher 当时做没做对）。

网页题只用真实页面：teacher 跑过的用它当时的快照，没跑过的用 curl 抓（`capture_pages.py --proxy`），存档进 `bank/web-archive/`，评测时由 `web-replay.mjs` 回放；没有存档的题，搜索返回空、抓取返回 404，和训练时的非网页题一致。原题库里手写假网页的题不用。

**和训练环境对齐**：评测用的 DSH 是训练数据所用的同一个源码提交（`dsh-8bd07339`，从未发布到 npm；`overlay-toolchain.sh` 把源码打的包覆盖到 npm 版工具链上），系统提示词和训练行逐字节相同（RWKV trace 在 `agent/trace/`，可随时核对）。

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
- 写 `/logs/agent/events.jsonl`（session / tool_call / tool_result / status / final 事件，DSH 的格式）和 `turns.json`，多轮题每轮写 `events-N.jsonl`、`final-N.txt`、`ws-N.json`；`diagnose.py` 和探针题读这些。
- `version()` 返回 `key value; ...` 格式，`report.py` 从这里读框架版本（commit 带 `*` 表示有未提交改动）：DSH 是 `dsh <版本>; plugin <commit>; eval <commit>; ...`，Pi 是 `pi <版本>; rwkv-pi <commit>; eval <commit>; ...`。

## 跑法

工具链包（Node + DSH + pnpm）不在容器里联网安装。npm 版本：

```bash
backends/dsh/build-toolchain.sh 0.2.2-alpha.3
```

默认的 `dsh-8bd07339`（训练用的源码版）由 `overlay-toolchain.sh` 生成，跑分服务器上由 `sync-server.sh` 自动完成。高并发时用 `prepare-toolchain.sh` 把工具链在宿主机解压一次、只读挂载进每个 trial（`calibrate.sh` 已经这样做），否则每个 trial 都要上传解压 237 MB。

多轮题的后续轮放在 `/rae/turns.json`，网页存档放在 `/rae/web.json`，agent 启动前框架会把它们取走并删除。每轮单独记录 `events-N.jsonl`、`final-N.txt`、`ws-N.json`（工作区哈希）。

跑分服务器（Docker 免密即可）：

```bash
scripts/sync-server.sh user@host /path/to/parent
```

```bash
ssh user@host 'cd /path/to/parent/rwkv-agent-eval && scripts/calibrate.sh http://<端点> 80 build/candidates 3'
```

`calibrate.sh` 先跑 `tasks/env-grep-probe`（DSH 自带 grep 不能用时直接停）。换 Pi 框架加 `BACKEND=pi CONTAINER_URL=http://<容器能访问的引擎地址>`，探针换成 `tasks/env-pi-probe`；Pi 要求锁定版本的 Lightning，详见 [backends/pi/README.md](backends/pi/README.md)。

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
- 每个 trial 的 `agent/provenance.json`：端点 `/v1/models` 原始回复、工具链包 sha256、是否挂载、回放插件 sha256、追加的 profile 配置、插件和本仓库的完整 HEAD、**未提交的 diff 和未跟踪文件列表**（`*` 的版本也能复原）、宿主平台。
- 每个 trial 的 `agent/trace/`：RWKV 每次请求的原始提示词和输出。
- job 目录的 `config.json`：命令行参数（端点等）。

同一配置两次运行的逐题结果会大量翻转（试点里 30 题两次通过的几乎不重叠），比较版本时每题至少跑 3 次。
