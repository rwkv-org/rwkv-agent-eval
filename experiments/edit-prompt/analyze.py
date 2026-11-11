"""Summarize the edit-prompt experiment: per variant, edit-tool failure rates and scores.

Usage (eval root): python3 experiments/edit-prompt/analyze.py runs/edit-prompt-<stamp>
Each variant dir holds one Harbor job (<variant>/<timestamp>/<trial>/...).
Score deltas are paired by task against `base` (mean over the task's trials), with a
task-level standard error.
"""
import collections
import glob
import json
import math
import re
import sys

ROOT = sys.argv[1].rstrip('/')
VARIANTS = ['base', 'desc', 'rule', 'both']


def trial_stats(d):
    s = collections.Counter()
    try:
        s['reward'] = float(open(d + 'verifier/reward.txt').read().strip())
        s['scored'] = 1
    except (OSError, ValueError):
        pass
    for f in glob.glob(d + 'agent/events-[0-9]*.jsonl'):
        calls = {}
        for line in open(f):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get('type') == 'tool_call':
                calls[e['callId']] = e['tool']
                s['calls'] += 1
                if e['tool'] in ('edit', 'write', 'read'):
                    s[e['tool']] += 1
            elif e.get('type') == 'tool_result' and calls.get(e.get('callId')) == 'edit':
                if e.get('status') == 'error':
                    s['edit_err'] += 1
                    r = e.get('result') or ''
                    if 'was not found' in r:
                        s['nf'] += 1
                    elif 'must differ' in r:
                        s['same'] += 1
                    else:
                        s['other_err'] += 1
    return s


def main():
    per = {}
    for v in VARIANTS:
        trials = {}
        for d in glob.glob(f'{ROOT}/{v}/*/*/'):
            if not glob.glob(d + 'agent'):
                continue
            task = d.rstrip('/').split('/')[-1].rsplit('__', 1)[0]
            trials[d] = (task, trial_stats(d))
        per[v] = trials
    base_task = task_means(per.get('base', {}))
    hdr = f"{'variant':7} {'trials':>6} {'score':>6} {'Δscore±se':>12} {'edits/t':>7} {'edit fail':>9} {'notfound':>8} {'same':>5} {'t w/ fail':>9} {'writes/t':>8} {'reads/t':>7}"
    print(hdr)
    for v in VARIANTS:
        trials = per[v]
        if not trials:
            continue
        tot = collections.Counter()
        tw = 0
        for _, s in trials.values():
            tot.update(s)
            tw += s['edit_err'] > 0
        n = len(trials)
        score = tot['reward'] / max(tot['scored'], 1)
        tm = task_means(trials)
        common = [t for t in tm if t in base_task]
        diffs = [tm[t] - base_task[t] for t in common]
        if len(diffs) > 1:
            mean = sum(diffs) / len(diffs)
            se = math.sqrt(sum((x - mean) ** 2 for x in diffs) / (len(diffs) - 1) / len(diffs))
            delta = f'{mean * 100:+.1f}±{se * 100:.1f}'
        else:
            delta = '-'
        e = max(tot['edit'], 1)
        print(f"{v:7} {n:>6} {score * 100:6.1f} {delta:>12} {tot['edit'] / n:7.2f} {tot['edit_err'] / e:9.1%} {tot['nf'] / e:8.1%} {tot['same']:>5} {tw:>9} {tot['write'] / n:8.2f} {tot['read'] / n:7.2f}")


def task_means(trials):
    by = collections.defaultdict(list)
    for task, s in trials.values():
        if s['scored']:
            by[task].append(s['reward'])
    return {t: sum(v) / len(v) for t, v in by.items()}


if __name__ == '__main__':
    main()
