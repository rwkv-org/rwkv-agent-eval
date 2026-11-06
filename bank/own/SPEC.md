# 自造题规范（bank/own/cases）

这里的题用来考 RWKV 模型在 DeepSeek Harness（DSH）里当 Agent 的能力，补齐开源题和训练题库剩下的题覆盖不到的能力块。
一道题一个 JSON 文件，文件名 = `id`。`bank/convert.py` 把它转成 Harbor 题，`bank/judge.py` 判分。

## 被测环境（题面必须和它一致）

- 模型：RWKV 7B，能力有限。题目要**清楚、有唯一正确答案**，难度靠任务本身（要找、要读、要串起来），不要靠文字游戏或陷阱。
- 工作目录：`/app`，里面就是 `files` 里的文件。
- 可用工具只有这 8 个：`bash`、`read`、`write`、`edit`、`glob`、`grep`、`web_search`、`web_fetch`。
  没有邮件、日历、计算器、天气、数据库、浏览器点击等工具。
- 一道题可以有多轮：每一轮是用户的一条消息，模型答完这一轮，下一轮才发出来，上下文保留。

## JSON 格式

```json
{
  "id": "own-rc-001",
  "category": "查找阅读-代码",
  "files": {"src/app.py": "...文件全文...", "README.md": "..."},
  "turns": [
    {"prompt": "用户第 1 轮的话", "expect": { ...本轮判据... }},
    {"prompt": "用户第 2 轮的话", "expect": { ... }}
  ],
  "expect": { ...整题判据（最后一轮结束后的文件状态）... },
  "reference": {
    "turns": [
      {"tools": ["grep", "read"], "final": "参考回复全文", "files": {}},
      {"tools": ["read", "edit"], "final": "...", "files": {"src/app.py": "改后的全文"}}
    ]
  },
  "provenance": {"author": "codex:gpt-6.1-sol", "batch": "<批次名>", "notes": "考点一句话"}
}
```

### 本轮判据 `turns[].expect`（都可选，至少要有一项能区分对错）

| 字段 | 含义 |
|---|---|
| `output_contains`: [..] | 回复必须包含每一项（大小写不敏感，忽略 `**`） |
| `output_contains_token`: true | 上一项按“完整词”匹配（`2` 不会匹配到 `12`、`2.5`），**答案是数字或短词时必须开** |
| `output_contains_any`: [..] | 包含其中任意一项即可：**把所有合理写法都列上**（中英文、全半角、带不带单位、`3`/`三`/`three`） |
| `output_contains_any_token`: true | 上一项按完整词匹配 |
| `output_excludes`: [..] | 回复不能包含（用来排除典型错误答案，比如被覆盖前的旧值） |
| `expected_number` + `tolerance` | 回复里要有这个数（±容差）；默认要求整条回复 ≤40 字符，加 `expected_number_in_text: true` 则允许在长回复里 |
| `required_tools`: [..] | 本轮必须调用过（`grep`/`read`/`glob`/`bash` 之间互相可替代，算“查看类”） |
| `forbidden_tools`: [..] | 本轮不能调用 |
| `require_active_no_call`: true | 本轮一个工具都不能调 |
| `unchanged_files`: [..] | 只读轮：这些文件本轮结束时必须和初始完全一样，且本轮不能调 write/edit |

### 整题判据 `expect`

| 字段 | 含义 |
|---|---|
| `files`: {path: {...}} | `equals`（全文相等，忽略结尾空白和 CRLF）、`contains`: [..]（包含这些片段）、`unchanged`: true、`absent`: true |
| `max_calls`: {tool: n} | 全题某工具最多调用 n 次 |

### 参考答案 `reference.turns`（每轮一项，必填）

- `tools`：一个合格 Agent 这一轮会调用的工具（按顺序，用于自检 `required_tools`）。
- `final`：一个合格回复的全文。
- `files`：这一轮结束后被改动/新建的文件全文（`null` 表示删除）。

## 自检（必须通过）

```bash
python3 bank/check_own.py bank/own/cases/<id>.json
```

检查：格式、参考答案必须判通过、什么都不做必须判不通过、题面不能和训练题库重复。**不通过的题不要留下**。

## 写题要求

1. **判据不能误杀**：答案的每种合理写法都要被接受。宁可多列 `output_contains_any` 的同义写法，也不要让正确回答因为措辞被判错。判据只卡**事实**，不卡格式（除非格式本身就是考点）。
2. **判据不能放水**：不看文件就猜不出答案。答案要来自 `files` 里的内容，用文件里**特有的**值（具体数字、名字、路径），不要用常识能猜到的值。
3. **文件要像真的项目**：名字、注释、目录结构像真实团队的代码/文档，不要出现“测试”“题目”“虚构”“fixture”“eval”之类字样，不要有占位符。日期不要晚于 2026 年。
4. **中英文**：约 60% 中文题面、40% 英文题面；文件内容可以中英混合，像真实项目。
5. **多轮**：约 35% 的题做 2–3 轮。后一轮要依赖前一轮的结果（追问、纠正、在前一轮基础上再做一步），不要把无关的问题拼在一起。
6. **难度梯度**：每批题里，约 30% 简单（一两次查看就能答）、50% 中等（要找几个地方、串起来）、20% 较难（要排除干扰项、跟踪调用链或覆盖关系）。在 `provenance.notes` 里写一句考点，并写 `"level": "easy|medium|hard"`。
7. 不要和别的题重复考同一个点；同一批里换着用不同的语言/项目类型/问题类型。
