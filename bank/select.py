#!/usr/bin/env python3
"""Pick the eval bank from calibration runs.

    python3 bank/select.py runs/calib-A [runs/calib-B ...] [--tasks build/candidates --tasks build/oss]
                           [--version v1] [--out bank/selection-v1.json] [--copy build/bank-v1]

Per task, the calibration pass count (k trials, environment errors left out)
puts it in one of three bins: flaky (some passed, some failed: the tasks that
tell two model versions apart), always (every trial passed) and never.

Per eval block, up to QUOTA[block] tasks: flaky first; then always and never,
each capped at EDGE (20%) of the quota (a floor and a ceiling to notice big
moves); never-pass tasks the teacher also failed are not picked but listed as
`suspect` (likely broken tasks, to be read by a person). Leftover room goes
to the remaining flaky, then never (teacher-solved), then always tasks.
Within a bin, tasks are drawn round-robin over training domains (category) so
sub-skills stay covered; order inside a domain is a fixed-seed shuffle.
Seen (already-trained) tasks are all kept as their own split.
"""
import argparse
import collections as C
import json
import random
import shutil
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUOTA = {
    'direct': 40, 'read-local': 50, 'read-code': 40, 'stat': 45, 'edit-data': 45, 'edit-code': 40,
    'code-fix': 40, 'web-local': 50, 'web-code': 15, 'search': 6,
    'code-fix-oss': 40, 'terminal': 30,
}
EDGE = 0.2
SEED = 20261106


# AgentTimeoutError is the model's failure (it ran out of time, usually looping): it scores 0.
# Other exceptions are environment errors: left out and re-run, not scored.
MODEL_FAILURES = {'AgentTimeoutError'}


def trials(job):
    by = C.defaultdict(list)
    for f in list(job.glob('*/result.json')) + list(job.glob('*/*/result.json')):
        r = json.loads(f.read_text())
        if 'task_name' not in r:
            continue
        exc = (r.get('exception_info') or {}).get('exception_type')
        if exc and exc not in MODEL_FAILURES:
            continue
        reward = ((r.get('verifier_result') or {}).get('rewards') or {}).get('reward') or 0
        by[r['task_name'].split('/')[-1]].append(float(reward) >= 1)
    return by


def round_robin(tasks, rng):
    by = C.defaultdict(list)
    for t in tasks:
        by[t['category']].append(t)
    for v in by.values():
        rng.shuffle(v)
    order, keys = [], sorted(by)
    while any(by.values()):
        for k in keys:
            if by[k]:
                order.append(by[k].pop())
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--tasks', action='append', default=[])
    ap.add_argument('--min-trials', type=int, default=3)
    ap.add_argument('--version', default='v1')
    ap.add_argument('--out', default='')
    ap.add_argument('--copy', default='', help='copy the picked task dirs here (a runnable bank)')
    a = ap.parse_args()
    dirs = [Path(d) for d in (a.tasks or [ROOT / 'build' / 'candidates', ROOT / 'build' / 'oss'])]
    res = C.defaultdict(list)
    for r in a.runs:
        for tid, xs in trials(Path(r)).items():
            res[tid] += xs
    tasks, where = [], {}
    for d in dirs:
        for toml in sorted(d.glob('*/task.toml')):
            m = tomllib.loads(toml.read_text()).get('metadata', {})
            tid = toml.parent.name
            xs = res.get(tid, [])
            where[tid] = toml.parent
            tasks.append({'id': tid, 'block': m.get('block', '?'), 'split': m.get('split', '?'),
                          'category': m.get('category') or m.get('source_dataset') or '?',
                          'teacher': m.get('teacher', '-'), 'turns': m.get('turns', 1),
                          'n': len(xs), 'passes': sum(xs)})
    rng = random.Random(SEED)
    picked, suspect, short = [], [], []
    for t in tasks:
        if t['n'] < a.min_trials:
            short.append(t['id'])
    for t in tasks:
        t['bin'] = ('flaky' if 0 < t['passes'] < t['n'] else 'always' if t['passes'] == t['n'] else 'never') \
            if t['n'] >= a.min_trials else 'uncalibrated'
        if t['bin'] == 'never' and t['teacher'] == 'failed':
            suspect.append(t['id'])
    seen = [t for t in tasks if t['split'] == 'seen' and t['bin'] != 'uncalibrated']
    picked += [dict(t, why='seen') for t in seen]
    report = {}
    for blk in sorted({t['block'] for t in tasks}):
        pool = [t for t in tasks if t['block'] == blk and t['split'] != 'seen' and t['bin'] != 'uncalibrated'
                and t['id'] not in suspect]
        q = QUOTA.get(blk, 0)
        bins = {b: round_robin([t for t in pool if t['bin'] == b], rng) for b in ('flaky', 'always', 'never')}
        # never: teacher-solved first (the task is known solvable)
        bins['never'].sort(key=lambda t: t['teacher'] != 'kept')
        edge = max(1, int(EDGE * q))
        take = bins['flaky'][:q] + bins['always'][:edge] + bins['never'][:edge]
        take = take[:q]
        left = [t for b in ('flaky', 'never', 'always') for t in bins[b] if t not in take]
        take += left[:q - len(take)]
        picked += [dict(t, why=t['bin']) for t in take]
        report[blk] = {'quota': q, 'pool': len(pool), 'picked': len(take),
                       **{b: sum(1 for t in take if t['bin'] == b) for b in ('flaky', 'always', 'never')},
                       'multi_turn': sum(1 for t in take if (t['turns'] or 1) > 1),
                       'pool_flaky': len(bins['flaky'])}
    print(f'{"block":13s} quota pool picked  flaky always never  multi-turn  (flaky in pool)')
    for blk, r in report.items():
        print(f'{blk:13s} {r["quota"]:5d} {r["pool"]:4d} {r["picked"]:6d}  {r["flaky"]:5d} {r["always"]:6d} {r["never"]:5d}'
              f'  {r["multi_turn"]:10d}  ({r["pool_flaky"]})')
    print(f'seen kept: {len(seen)}; total picked: {len(picked)}; suspect (teacher and model both fail): '
          f'{len(suspect)}; not yet calibrated (<{a.min_trials} trials): {len(short)}')
    out = Path(a.out or ROOT / 'bank' / f'selection-{a.version}.json')
    out.write_text(json.dumps({
        'version': a.version, 'runs': a.runs, 'seed': SEED, 'quota': QUOTA, 'edge': EDGE, 'report': report,
        'tasks': [{k: t[k] for k in ('id', 'block', 'split', 'category', 'teacher', 'turns', 'n', 'passes', 'why')}
                  for t in sorted(picked, key=lambda t: (t['block'], t['id']))],
        'suspect': sorted(suspect),
    }, ensure_ascii=False, indent=1))
    print(f'wrote {out}')
    if a.copy:
        dst = Path(a.copy)
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for t in picked:
            shutil.copytree(where[t['id']], dst / t['id'])
        print(f'copied {len(picked)} tasks to {dst}')


if __name__ == '__main__':
    main()
