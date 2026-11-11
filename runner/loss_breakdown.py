#!/usr/bin/env python3
"""Where a run loses points: per block, per failure kind, per tool error, per plugin intervention.

    python3 runner/loss_breakdown.py --tasks build/bank-full-1019 \
        --run new=JOB[,JOB...] [--run old=JOB ...] --out runs/loss

A run may pool several Harbor jobs of the same model (comma-separated), so each task
gets more trials. The first --run is the one analysed in depth; later runs are only
compared on scores. Writes <out>.json with every table; the report is written by hand.

Per trial it reads: the (rejudged) reward and judge failures (runner/attribution.py),
agent/events-*.jsonl (tool calls, tool errors), agent/trace/*.jsonl (the plugin's
decisions: duplicate-call retries, forced close-outs, re-asks after unparseable output,
generations cut by the length limit) and agent/turns.json.
"""
import argparse
import collections as C
import json
import re
import tomllib
from pathlib import Path

from attribution import failure_kind, load

ERR_TEXT = [  # tool errors without a DSH error code, labelled by their text
    (r'timed out|timeout', 'timeout'), (r'exit code|exited with', 'nonzero-exit'),
    (r'blocked|duplicate', 'blocked'), (r'', 'other'),
]


def error_label(res):
    code = (res.get('error') or {}).get('code')
    if code:
        return code
    text = str(res.get('result') or '')[:300].lower()
    return next(label for pat, label in ERR_TEXT if re.search(pat, text))


def read_jsonl(paths):
    for p in paths:
        for line in p.read_text(errors='replace').splitlines():
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                pass


MAX_STEPS = 12
CHANGE_KINDS = {'tests-failed', 'file-result-wrong'}


def cause(f, tools, kind):
    """First matching proximate cause of a failed trial (heuristic, in priority order)."""
    if kind == 'timeout':
        return 'timeout'
    if f.get('outcome:re-ask') or f.get('cut-by-length'):
        return 'output unparseable / cut by length'
    if f.get('outcome:closeout'):
        return 'loop guard: repeated identical call, forced close-out'
    if f.get('max-steps'):
        return 'hit 12-tool-call limit, forced close-out'
    if kind in CHANGE_KINDS and f.get('edit-unresolved'):
        return 'edit failed and never fixed'
    if kind in CHANGE_KINDS and not f.get('changes'):
        return 'never changed a file'
    if kind in {'no-required-tool', 'no-web-search', 'no-web-fetch', 'used-forbidden-tool',
                'tools-when-none-needed', 'wrote-in-read-only-turn', 'too-many-calls'}:
        return 'tool choice: ' + kind
    if kind == 'tests-failed':
        return 'changed files, tests still fail' + ('' if f.get('ran-tests') else ' (never ran tests)')
    return kind


def trial_facts(t):
    d = t['dir']
    calls, f = {}, C.Counter()
    tools, errors = C.Counter(), C.Counter()
    unresolved = set()  # files whose latest edit attempt failed
    for e in read_jsonl(sorted((d / 'agent').glob('events-*.jsonl'),
                               key=lambda p: int(re.search(r'-(\d+)\.jsonl$', p.name).group(1)))):
        if e.get('type') == 'tool_call':
            calls[e['callId']] = e
            tools[e['tool']] += 1
        elif e.get('type') == 'tool_result':
            c = calls.get(e.get('callId')) or {}
            tool, inp = c.get('tool', '?'), c.get('input') or {}
            path = str(inp.get('file_path', ''))
            if e.get('status') == 'error':
                errors[(tool, error_label(e))] += 1
                if tool == 'edit':
                    unresolved.add(path)
            elif tool in ('edit', 'write'):
                f['changes'] += 1
                unresolved.discard(path)
            elif tool == 'bash':
                m = re.search(r'\[exit code: (-?\d+)\]\s*$', str(e.get('result') or ''))
                if m and m.group(1) != '0':
                    f['bash-nonzero'] += 1
                    if m.group(1) == '127':
                        f['bash-not-found'] += 1
                cmd = str(inp.get('command', ''))
                if re.search(r'pytest|unittest|npm (run )?test|node --test|\btest\b|jest|mocha|make check', cmd):
                    f['ran-tests'] += 1
    f['edit-unresolved'] = len(unresolved)
    for tr in sorted((d / 'agent' / 'trace').glob('*.jsonl')):
        # one trace per user turn (one headless process); the plugin stops tools at maxSteps (12)
        tool_steps = sum(1 for e in read_jsonl([tr]) if e.get('stage') == 'step' and str(e.get('decision', '')).startswith('tool'))
        if tool_steps >= MAX_STEPS:
            f['max-steps'] += 1
    for e in read_jsonl(sorted((d / 'agent' / 'trace').glob('*.jsonl'))):
        if e.get('stage') == 'decision':
            f['decisions'] += 1
            f['outcome:' + str(e.get('outcome'))] += 1
            if e.get('finish') == 'length':
                f['cut-by-length'] += 1
    try:
        turns = json.loads((d / 'agent' / 'turns.json').read_text())
    except (OSError, json.JSONDecodeError):
        turns = {}
    fail_turn = None
    try:
        det = json.loads((d / 'verifier' / 'details.json').read_text())
        fail_turn = next((x.get('turn') for x in det.get('turns') or [] if x.get('failures')), None)
    except (OSError, json.JSONDecodeError):
        pass
    passed = t['reward'] >= 1
    return {
        'pass': passed, 'reward': t['reward'], 'kind': failure_kind(t), 'cause': None if passed else cause(f, tools, failure_kind(t)),
        'tools': dict(tools), 'errors': {f'{a}:{b}': n for (a, b), n in errors.items()},
        'plugin': dict(f), 'turns': turns.get('turns', 1), 'ran': turns.get('ran'), 'fail_turn': fail_turn,
        'dir': str(d),
    }


def pooled(spec):
    out = {}
    for job in spec.split(','):
        for tid, ts in load(job).items():
            out.setdefault(tid, []).extend(ts)
    return out


def rate(xs):
    return sum(xs) / len(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tasks', action='append', default=[])
    ap.add_argument('--run', action='append', required=True, help='NAME=JOB[,JOB...]')
    ap.add_argument('--out', default='runs/loss')
    a = ap.parse_args()
    meta = {}
    for d in a.tasks:
        for t in Path(d).glob('*/task.toml'):
            meta.setdefault(t.parent.name, tomllib.loads(t.read_text()).get('metadata', {}))
    runs = {}
    for r in a.run:
        name, spec = r.split('=', 1)
        runs[name] = pooled(spec)
    main_name = next(iter(runs))
    ids = sorted(set.intersection(*(set(r) for r in runs.values())) & set(meta))
    trials = []  # main run, every trial with its task metadata
    task_score = {n: {} for n in runs}
    for tid in ids:
        m = meta[tid]
        for n, r in runs.items():
            task_score[n][tid] = rate([t['reward'] >= 1 for t in r[tid]])
        for t in runs[main_name][tid]:
            trials.append({'task': tid, 'block': m.get('block', '?'), 'domain': m.get('category') or m.get('source_dataset') or '?',
                           'split': m.get('split', '?'), 'nturns': m.get('turns', 1), **trial_facts(t)})

    def by(key):
        groups = C.defaultdict(list)
        for t in trials:
            groups[key(t)].append(t)
        return groups

    total_lost = sum(1 - task_score[main_name][t] for t in ids)
    blocks = {}
    for blk, ts in sorted(by(lambda t: t['block']).items()):
        tids = sorted({t['task'] for t in ts})
        lost = sum(1 - task_score[main_name][t] for t in tids)
        scores = {n: rate([task_score[n][t] for t in tids]) for n in runs}
        per = [task_score[main_name][t] for t in tids]
        blocks[blk] = {'tasks': len(tids), 'trials': len(ts), 'score': scores, 'lost_tasks': lost,
                       'lost_share': lost / total_lost, 'all_fail': sum(s == 0 for s in per),
                       'flaky': sum(0 < s < 1 for s in per), 'all_pass': sum(s == 1 for s in per),
                       'kinds': dict(C.Counter(t['kind'] for t in ts if not t['pass']).most_common()),
                       'causes': dict(C.Counter(t['cause'] for t in ts if not t['pass']).most_common())}
    turns = {}
    for k, ts in sorted(by(lambda t: 'multi' if t['nturns'] > 1 else 'single').items()):
        turns[k] = {'trials': len(ts), 'pass': rate([t['pass'] for t in ts]),
                    'fail_turn': dict(C.Counter(t['fail_turn'] for t in ts if not t['pass']).most_common())}
    kinds = dict(C.Counter(t['kind'] for t in trials if not t['pass']).most_common())
    causes = dict(C.Counter(t['cause'] for t in trials if not t['pass']).most_common())

    # tools: calls, error rate, error labels; pass rate of trials with / without that error
    tool_tab = {}
    all_tools = C.Counter()
    for t in trials:
        all_tools.update(t['tools'])
    for tool, n in all_tools.most_common():
        errs = C.Counter()
        for t in trials:
            for k, v in t['errors'].items():
                if k.split(':', 1)[0] == tool:
                    errs[k.split(':', 1)[1]] += v
        users = [t for t in trials if t['tools'].get(tool)]
        with_err = [t for t in users if any(k.split(':', 1)[0] == tool for k in t['errors'])]
        without = [t for t in users if t not in with_err]
        tool_tab[tool] = {'calls': n, 'errors': sum(errs.values()), 'error_rate': sum(errs.values()) / n,
                          'labels': dict(errs.most_common()), 'trials_using': len(users),
                          'trials_with_error': len(with_err), 'pass_with_error': rate([t['pass'] for t in with_err]),
                          'pass_without_error': rate([t['pass'] for t in without])}
    plugin = {}
    for key in ['outcome:duplicate-retry', 'outcome:closeout', 'outcome:re-ask', 'outcome:rejected blocked', 'cut-by-length',
                'max-steps', 'edit-unresolved', 'bash-nonzero', 'bash-not-found', 'ran-tests']:
        hit = [t for t in trials if t['plugin'].get(key)]
        plugin[key] = {'events': sum(t['plugin'].get(key, 0) for t in trials), 'trials': len(hit),
                       'pass_hit': rate([t['pass'] for t in hit]),
                       'pass_not_hit': rate([t['pass'] for t in trials if not t['plugin'].get(key)])}
    steps = {}
    for label, ts in [('passed', [t for t in trials if t['pass']]), ('failed', [t for t in trials if not t['pass']])]:
        calls = sorted(sum(t['tools'].values()) for t in ts)
        steps[label] = {'trials': len(ts), 'no_tools': rate([not t['tools'] for t in ts]),
                        'median_calls': calls[len(calls) // 2] if calls else None,
                        'calls_ge_20': rate([c >= 20 for c in calls])}
    movers = {}
    if len(runs) > 1:
        other = [n for n in runs if n != main_name][0]
        for blk in blocks:
            tids = [t for t in ids if meta[t].get('block') == blk]
            movers[blk] = {'worse': sorted(t for t in tids if task_score[main_name][t] - task_score[other][t] <= -0.5),
                           'better': len([t for t in tids if task_score[main_name][t] - task_score[other][t] >= 0.5])}
    out = {'runs': {n: r for n, r in zip(runs, [x.split('=', 1)[1] for x in a.run])}, 'tasks': len(ids),
           'trials': len(trials), 'score': {n: rate(list(task_score[n].values())) for n in runs},
           'total_lost_tasks': total_lost, 'causes': causes, 'blocks': blocks, 'turns': turns, 'kinds': kinds, 'tools': tool_tab,
           'plugin': plugin, 'steps': steps, 'movers_vs_' + ([n for n in runs if n != main_name] or ['-'])[0]: movers,
           'per_task': {t: {n: task_score[n][t] for n in runs} | {'block': meta[t].get('block')} for t in ids},
           'per_trial': [{k: v for k, v in t.items()} for t in trials]}
    Path(a.out + '.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: out[k] for k in ['score', 'tasks', 'trials', 'total_lost_tasks', 'causes', 'kinds', 'turns', 'plugin', 'steps']}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
