#!/usr/bin/env python3
"""Data-level attribution: line eval results up with the training mix.

    python3 runner/attribution.py <base run> <adapter run> --tasks DIR [--tasks DIR ...]
            [--mix bank/mix-domains.json] [--out runs/attribution]

Runs are Harbor job dirs, or several joined by '+' (later jobs replace earlier
timed-out trials of a task, as in runner/dashboard.py). Writes <out>.json (every
table) and <out>.md (readable report). Per task: the training domain (task.toml
category; the mix's block files are named after these domains), eval block,
split (seen / heldout / oss), and both runs' mean reward. Per trial, from the
judge's details.json and the agent's events: the failure kind, and behaviour
features (no tool call at all, web_search vs web_fetch on web tasks, fetch 404s,
tool errors, repeated identical calls, timeouts).

Tables:
  domains      per training domain: mix rows/cases, tasks, base, adapter, delta (paired ± 95%)
  blocks       per eval block x split
  failures     per block: share of failed trials by failure kind, base vs adapter
  behaviour    per block: behaviour rates, base vs adapter
  movers       tasks whose mean moved by >= 0.5, with the adapter's failure kinds
"""
import argparse
import collections as C
import json
import math
import tomllib
from pathlib import Path

from rescore import rejudged_reward

ROOT = Path(__file__).resolve().parents[1]
MODEL_FAILURES = {'AgentTimeoutError'}
VIEW = {'read', 'grep', 'glob', 'bash'}


def trial_dirs(job):
    for f in list(job.glob('*/result.json')) + list(job.glob('*/*/result.json')):
        r = json.loads(f.read_text())
        if 'task_name' in r:
            yield r, f.parent


def load(spec):
    out = {}
    for part in spec.split('+'):
        for r, d in trial_dirs(Path(part)):
            tid = r['task_name'].split('/')[-1]
            exc = (r.get('exception_info') or {}).get('exception_type')
            reward = rejudged_reward(d, float(((r.get('verifier_result') or {}).get('rewards') or {}).get('reward') or 0))
            old = out.setdefault(tid, [])
            i = next((k for k, o in enumerate(old) if o['exc'] in MODEL_FAILURES), None)
            if i is not None:
                old.pop(i)
            old.append({'exc': exc, 'reward': reward, 'dir': d})
    for ts in out.values():
        ts[:] = [t for t in ts if not t['exc'] or t['exc'] in MODEL_FAILURES]  # drop environment errors
    return {k: v for k, v in out.items() if v}


def failure_kind(t):
    if t['exc'] in MODEL_FAILURES:
        return 'timeout'
    if t['reward'] >= 1:
        return None
    try:
        det = json.loads((t['dir'] / 'verifier' / 'details.json').read_text())
    except (OSError, json.JSONDecodeError):
        return 'tests-failed'  # open-source tasks: their own test script, no judge details
    msgs = [m for turn in det.get('turns') or [] for m in turn.get('failures') or []]
    case = det.get('case') or []
    msgs += case if isinstance(case, list) else case.get('failures') or []
    order = [
        ('turn not run', 'turn-not-run'),
        ('required tool web_fetch', 'no-web-fetch'),
        ('required tool web_search', 'no-web-search'),
        ('required tool', 'no-required-tool'),
        ('forbidden tool', 'used-forbidden-tool'),
        ('no-call turn', 'tools-when-none-needed'),
        ('read-only turn', 'wrote-in-read-only-turn'),
        ('program check', 'tests-failed'),
        ('output ', 'answer-wrong'), ('no figure', 'answer-wrong'),
        ('should be absent', 'file-result-wrong'), (' missing', 'file-result-wrong'), (' changed', 'file-result-wrong'),
        ('differs from expected', 'file-result-wrong'), (' lacks ', 'file-result-wrong'),
        (' times (max', 'too-many-calls'),
    ]
    for key, kind in order:
        if any(m.startswith(key) or (key.startswith(' ') and key in m and not m.startswith('output')) or
               (not key.startswith(' ') and key in m) for m in msgs):
            return kind
    return 'other'


def behaviour(t):
    ev = []
    for f in sorted((t['dir'] / 'agent').glob('events-*.jsonl')):
        for line in f.read_text().splitlines():
            try:
                ev.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    calls = [e for e in ev if e.get('type') == 'tool_call']
    res = [e for e in ev if e.get('type') == 'tool_result']
    sig = C.Counter(json.dumps([e.get('tool'), e.get('input')], sort_keys=True, ensure_ascii=False) for e in calls)
    tools = C.Counter(e.get('tool') for e in calls)
    return {
        'calls': len(calls),
        'no_tools': not calls,
        'tool_errors': sum(1 for e in res if e.get('status') == 'error'),
        'fetch_404': sum(1 for e in res if e.get('status') == 'error' and '404' in json.dumps(e.get('result'))[:300]),
        'repeats': sum(n - 1 for n in sig.values() if n > 1),
        'web_search': tools.get('web_search', 0), 'web_fetch': tools.get('web_fetch', 0),
        'view': sum(tools.get(x, 0) for x in VIEW), 'edits': tools.get('edit', 0) + tools.get('write', 0),
    }


def mean_se(xs):
    n = len(xs)
    if not n:
        return None, None
    m = sum(xs) / n
    return m, (math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1) / n) if n > 1 else None)


def fmt(m, se=None, signed=False):
    if m is None:
        return '-'
    s = f'{100 * m:+.1f}' if signed else f'{100 * m:.1f}'
    return s + (f' ±{196 * se:.1f}' if se is not None else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('adapter')
    ap.add_argument('--tasks', action='append', default=[])
    ap.add_argument('--mix', default=str(ROOT / 'bank' / 'mix-domains.json'))
    ap.add_argument('--out', default='runs/attribution')
    a = ap.parse_args()
    meta = {}
    for d in a.tasks:
        for t in Path(d).glob('*/task.toml'):
            meta.setdefault(t.parent.name, tomllib.loads(t.read_text()).get('metadata', {}))
    mix = json.loads(Path(a.mix).read_text())
    runs = {'base': load(a.base), 'adapter': load(a.adapter)}
    ids = sorted(set(runs['base']) & set(runs['adapter']) & set(meta))
    task = {}
    for tid in ids:
        m = meta[tid]
        row = {'domain': m.get('category') or m.get('source_dataset') or '?', 'block': m.get('block', '?'),
               'split': m.get('split', '?'), 'turns': m.get('turns', 1)}
        for k, r in runs.items():
            ts = r[tid]
            row[k] = sum(t['reward'] >= 1 for t in ts) / len(ts)
            row[k + '_fail'] = C.Counter(filter(None, (failure_kind(t) for t in ts)))
            row[k + '_beh'] = [behaviour(t) for t in ts]
        task[tid] = row

    def agg(group):
        out = {}
        for key in sorted({group(r) for r in task.values()}):
            rs = [r for r in task.values() if group(r) == key]
            b, _ = mean_se([r['base'] for r in rs]); ad, _ = mean_se([r['adapter'] for r in rs])
            d, dse = mean_se([r['adapter'] - r['base'] for r in rs])
            out[key] = {'n': len(rs), 'base': b, 'adapter': ad, 'delta': d, 'delta_se': dse}
        return out
    domains = agg(lambda r: r['domain'])
    for k, v in domains.items():
        v['mix_rows'] = mix['rows'].get(k, 0); v['mix_cases'] = mix['cases'].get(k, 0)
    blocks = agg(lambda r: f"{r['block']}|{r['split']}")
    failures, beh = {}, {}
    for blk in sorted({r['block'] for r in task.values()}):
        rs = [r for r in task.values() if r['block'] == blk]
        failures[blk], beh[blk] = {}, {}
        for k in runs:
            c = sum((r[k + '_fail'] for r in rs), C.Counter())
            tot = sum(c.values())
            failures[blk][k] = {kind: n / tot for kind, n in c.most_common()} if tot else {}
            failures[blk][k + '_n'] = tot
            bs = [b for r in rs for b in r[k + '_beh']]
            web = [b for r, bb in ((r, r[k + '_beh']) for r in rs) if r['block'].startswith('web') for b in bb]
            beh[blk][k] = {
                'trials': len(bs),
                'no_tools': sum(b['no_tools'] for b in bs) / len(bs),
                'calls': sum(b['calls'] for b in bs) / len(bs),
                'tool_error_rate': sum(b['tool_errors'] for b in bs) / max(1, sum(b['calls'] for b in bs)),
                'repeat_rate': sum(b['repeats'] for b in bs) / max(1, sum(b['calls'] for b in bs)),
                'fetched': (sum(b['web_fetch'] > 0 for b in web) / len(web)) if web else None,
                'searched': (sum(b['web_search'] > 0 for b in web) / len(web)) if web else None,
                'fetch_404': (sum(b['fetch_404'] for b in web) / len(web)) if web else None,
            }
    movers = sorted(({'id': tid, 'domain': r['domain'], 'block': r['block'], 'split': r['split'],
                      'base': r['base'], 'adapter': r['adapter'], 'adapter_fail': dict(r['adapter_fail']),
                      'base_fail': dict(r['base_fail'])}
                     for tid, r in task.items() if abs(r['adapter'] - r['base']) >= 0.5),
                    key=lambda x: x['adapter'] - x['base'])
    report = {'base': a.base, 'adapter': a.adapter, 'tasks': len(task), 'mix': a.mix,
              'domains': domains, 'blocks': blocks, 'failures': failures, 'behaviour': beh, 'movers': movers,
              'per_task': {k: {**{x: v[x] for x in ('domain', 'block', 'split', 'base', 'adapter')},
                               'adapter_fail': dict(v['adapter_fail']), 'base_fail': dict(v['base_fail'])}
                           for k, v in task.items()}}
    Path(a.out + '.json').write_text(json.dumps(report, ensure_ascii=False, indent=1))

    L = [f'# 数据层面归因（自动生成）', '', f'- 基模：`{a.base}`', f'- adapter：`{a.adapter}`',
         f'- 题数：{len(task)}（两边都有成绩的题）；分数为每题平均，差值为同题配对差 ±95%', '',
         '## 按训练领域', '', '| 训练领域 | mix 行数 | mix 题数 | 评测题数 | 基模 | adapter | 差值 |', '|---|--:|--:|--:|--:|--:|--:|']
    for k, v in sorted(domains.items(), key=lambda kv: -kv[1]['mix_rows']):
        L.append(f"| {k} | {v['mix_rows']} | {v['mix_cases']} | {v['n']} | {fmt(v['base'])} | {fmt(v['adapter'])} | {fmt(v['delta'], v['delta_se'], True)} |")
    L += ['', '## 按能力块 × 是否训练过', '', '| 能力块 | split | 题数 | 基模 | adapter | 差值 |', '|---|---|--:|--:|--:|--:|']
    for k, v in blocks.items():
        b, s = k.split('|')
        L.append(f"| {b} | {s} | {v['n']} | {fmt(v['base'])} | {fmt(v['adapter'])} | {fmt(v['delta'], v['delta_se'], True)} |")
    L += ['', '## 失败类型（占失败 trial 的比例）', '']
    for blk, f in failures.items():
        for k in runs:
            top = ', '.join(f'{kind} {100 * p:.0f}%' for kind, p in list(f[k].items())[:5])
            L.append(f"- **{blk}** {k}（{f[k + '_n']} 次失败）：{top}")
    L += ['', '## 行为特征', '', '| 能力块 | 模型 | 不调工具 | 平均调用 | 工具报错率 | 重复调用率 | 网页题打开网页 | 网页题用搜索 | 每次 404 |',
          '|---|---|--:|--:|--:|--:|--:|--:|--:|']
    for blk, bb in beh.items():
        for k in runs:
            x = bb[k]
            L.append(f"| {blk} | {k} | {100 * x['no_tools']:.0f}% | {x['calls']:.1f} | {100 * x['tool_error_rate']:.0f}% | "
                     f"{100 * x['repeat_rate']:.0f}% | {fmt(x['fetched'])} | {fmt(x['searched'])} | "
                     f"{'-' if x['fetch_404'] is None else round(x['fetch_404'], 2)} |")
    L += ['', f'## 变化最大的题（|差| ≥ 0.5，共 {len(movers)} 道；完整列表见 JSON）', '']
    for m in movers[:25] + (['…'] if len(movers) > 50 else []) + movers[-25:]:
        if m == '…':
            L.append('- …'); continue
        L.append(f"- {m['id']}（{m['domain']}，{m['split']}）：{fmt(m['base'])} → {fmt(m['adapter'])}；adapter 失败：{m['adapter_fail'] or '-'}")
    Path(a.out + '.md').write_text('\n'.join(L) + '\n')
    print(f'wrote {a.out}.json and {a.out}.md ({len(task)} tasks)')


if __name__ == '__main__':
    main()
