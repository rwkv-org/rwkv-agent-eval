#!/usr/bin/env python3
"""Compact per-task digests of the tasks both runs score 0 on (the "hard" set).

    python3 runner/hard_digest.py <base run> <adapter run> --tasks DIR [--tasks DIR ...]
            [--out runs/hard-digest.jsonl] [--max-score 0]

Runs are Harbor job dirs or several joined by '+' (same merging as attribution.py).
One JSON line per task whose mean reward is <= --max-score in both runs:
the instruction, category, what the judge checks (expect.json / test names),
and for every trial of both runs: exception, failure kind, judge messages,
the tool-call sequence (tool, short input, result status, short result),
thinking volume, the final answer (truncated) and the test output tail.
Meant to be read by a person or another model to name the missing ability.
"""
import argparse
import json
import tomllib
from pathlib import Path

from attribution import failure_kind, load


def cut(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f'…[+{len(s) - n}]'


def events(d):
    ev = []
    for f in sorted((d / 'agent').glob('events-*.jsonl')) or [d / 'agent' / 'events.jsonl']:
        if f.exists():
            for line in f.read_text(errors='replace').splitlines():
                try:
                    ev.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return ev


def trial_digest(t):
    d = t['dir']
    ev = events(d)
    steps, think = [], []
    results = {e.get('callId'): e for e in ev if e.get('type') == 'tool_result'}
    turn = 1
    for e in ev:
        if e.get('type') == 'status' and e.get('phase') == 'turn_start':
            turn = e.get('turn', turn)
        elif e.get('type') == 'thinking':
            think.append(len(e.get('text') or ''))
        elif e.get('type') == 'tool_call':
            r = results.get(e.get('callId')) or {}
            steps.append({'turn': turn, 'tool': e.get('tool'), 'in': cut(e.get('input'), 240),
                          'ok': r.get('status'), 'out': cut(r.get('result'), 240)})
    finals = [e.get('text') or '' for e in ev if e.get('type') == 'final']
    try:
        det = json.loads((d / 'verifier' / 'details.json').read_text())
    except (OSError, json.JSONDecodeError):
        det = None
    stdout = d / 'verifier' / 'test-stdout.txt'
    return {
        'reward': t['reward'], 'exc': t['exc'], 'kind': failure_kind(t),
        'judge': det,
        'test_tail': cut(stdout.read_text(errors='replace')[-1500:], 1500) if stdout.exists() and not det else None,
        'steps': steps[:60], 'n_steps': len(steps),
        'think_chars': sum(think), 'think_max': max(think, default=0),
        'finals': [cut(f, 700) for f in finals],
    }


def task_info(tdir):
    info = {'instruction': cut((tdir / 'instruction.md').read_text(errors='replace'), 2500)}
    try:
        info['category'] = tomllib.loads((tdir / 'task.toml').read_text()).get('metadata', {}).get('category')
    except (OSError, tomllib.TOMLDecodeError):
        pass
    exp = tdir / 'tests' / 'expect.json'
    if exp.exists():
        info['expect'] = cut(exp.read_text(errors='replace'), 2500)
    tests = tdir / 'tests'
    if tests.is_dir():
        info['test_files'] = sorted(p.name for p in tests.iterdir())
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('adapter')
    ap.add_argument('--tasks', action='append', required=True)
    ap.add_argument('--out', default='runs/hard-digest.jsonl')
    ap.add_argument('--max-score', type=float, default=0.0)
    a = ap.parse_args()
    dirs = {}
    for root in a.tasks:
        for p in Path(root).iterdir():
            if (p / 'instruction.md').exists():
                dirs.setdefault(p.name, p)
    base, adapter = load(a.base), load(a.adapter)
    mean = lambda ts: sum(t['reward'] for t in ts) / len(ts)
    n = 0
    with open(a.out, 'w') as f:
        for tid in sorted(set(base) & set(adapter) & set(dirs)):
            if mean(base[tid]) > a.max_score or mean(adapter[tid]) > a.max_score:
                continue
            rec = {'task': tid, **task_info(dirs[tid]),
                   'base': [trial_digest(t) for t in base[tid]],
                   'adapter': [trial_digest(t) for t in adapter[tid]]}
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + '\n')
            n += 1
    print(f'{n} tasks -> {a.out}')


if __name__ == '__main__':
    main()
