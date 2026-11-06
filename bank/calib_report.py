#!/usr/bin/env python3
"""Calibration summary of a Harbor job: per task, how many of its k trials
passed; per eval block, how tasks spread over 0..k passes.

    python3 bank/calib_report.py runs/calib-<time> [--tasks build/candidates] [--out calib.jsonl]

Task metadata (block, split, source, teacher, turns) comes from each task's
task.toml under --tasks. Trials that raised (environment / agent errors) are
counted apart: they say nothing about the model and are re-run, not scored.
"""
import argparse
import collections as C
import json
import tomllib
from pathlib import Path


def load_trials(job):
    by = C.defaultdict(list)
    for f in job.glob('*/result.json'):
        r = json.loads(f.read_text())
        if 'task_name' not in r:
            continue  # the job-level result.json
        tid = r['task_name'].split('/')[-1]
        exc = (r.get('exception_info') or {}).get('exception_type')
        reward = ((r.get('verifier_result') or {}).get('rewards') or {}).get('reward')
        by[tid].append({'exc': exc, 'reward': reward, 'dir': f.parent.name})
    return by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('job')
    ap.add_argument('--tasks', default='build/candidates')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    job, tasks = Path(a.job), Path(a.tasks)
    trials = load_trials(job)
    meta = {}
    for t in tasks.iterdir():
        if (t / 'task.toml').exists():
            meta[t.name] = tomllib.loads((t / 'task.toml').read_text()).get('metadata', {})
    rows = []
    for tid, m in sorted(meta.items()):
        ts = trials.get(tid, [])
        good = [x for x in ts if not x['exc']]
        rows.append({'id': tid, 'block': m.get('block', '?'), 'split': m.get('split', '?'),
                     'source': m.get('source', '?'), 'teacher': m.get('teacher', '?'),
                     'turns': m.get('turns', 1), 'n': len(good), 'errors': len(ts) - len(good),
                     'passes': sum(1 for x in good if (x['reward'] or 0) >= 1)})
    done = [r for r in rows if r['n'] or r['errors']]
    print(f'{job}: {sum(r["n"] for r in rows)} scored trials, {sum(r["errors"] for r in rows)} errored, '
          f'{len(done)}/{len(rows)} tasks started')
    exc = C.Counter(x['exc'] for ts in trials.values() for x in ts if x['exc'])
    if exc:
        print('errors:', dict(exc.most_common(8)))
    print(f'\n{"block":11s} {"tasks":>5s} {"done":>5s}   passes out of 3: 0 / 1 / 2 / 3     pass rate')
    for blk in sorted({r['block'] for r in rows}):
        rs = [r for r in rows if r['block'] == blk]
        full = [r for r in rs if r['n'] >= 3]
        dist = C.Counter(min(r['passes'], 3) for r in full)
        rate = sum(r['passes'] for r in full) / max(1, sum(r['n'] for r in full))
        print(f'{blk:11s} {len(rs):5d} {len(full):5d}   {dist[0]:4d} {dist[1]:4d} {dist[2]:4d} {dist[3]:4d}      {rate:6.1%}')
    if a.out:
        Path(a.out).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))


if __name__ == '__main__':
    main()
