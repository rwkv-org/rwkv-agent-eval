#!/usr/bin/env python3
"""Top up eval blocks to a target size with calibrated held-out candidates not picked yet.

    python3 bank/fill_blocks.py runs/calib-A [--have bank/selection-v1-main.json ...]
            [--target 75] [--tasks build/candidates] [--out bank/selection-v1-fill.json] [--copy build/bank-v1-fill]

Same bins and order as bank/pick.py (flaky, then never with the teacher solving it,
then always, alternating never and always; round-robin over training domains, fixed seed), skipping seen tasks,
suspects (model and teacher both fail) and tasks already in a --have selection.
Only blocks listed in TOP_UP are filled: the other blocks get new cases instead.
"""
import argparse
import json
import random
import shutil
import tomllib
from pathlib import Path

from pick import SEED, round_robin, trials

ROOT = Path(__file__).resolve().parents[1]
TOP_UP = ['direct', 'read-local', 'stat', 'edit-data', 'edit-code']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--have', action='append', default=[])
    ap.add_argument('--target', type=int, default=75)
    ap.add_argument('--tasks', default=str(ROOT / 'build' / 'candidates'))
    ap.add_argument('--out', default=str(ROOT / 'bank' / 'selection-v1-fill.json'))
    ap.add_argument('--copy', default='')
    a = ap.parse_args()
    have = {}
    for s in a.have or [str(ROOT / 'bank' / 'selection-v1-main.json')]:
        d = json.loads(Path(s).read_text())
        for t in d['tasks']:
            have[t['id']] = t['block']
        suspect = set(d.get('suspect') or [])
    res = {}
    for r in a.runs:
        for tid, xs in trials(Path(r)).items():
            res.setdefault(tid, []).extend(xs)
    rng = random.Random(SEED + 1)
    picked, report = [], {}
    tasks = []
    for toml in sorted(Path(a.tasks).glob('*/task.toml')):
        m = tomllib.loads(toml.read_text()).get('metadata', {})
        xs = res.get(toml.parent.name, [])
        tasks.append({'id': toml.parent.name, 'block': m.get('block'), 'split': m.get('split'),
                      'category': m.get('category') or '?', 'teacher': m.get('teacher', '-'),
                      'turns': m.get('turns', 1), 'n': len(xs), 'passes': sum(xs)})
    for blk in TOP_UP:
        need = a.target - sum(1 for b in have.values() if b == blk)
        pool = [t for t in tasks if t['block'] == blk and t['split'] == 'heldout' and t['id'] not in have
                and t['id'] not in suspect and t['n'] >= 3]
        for t in pool:
            t['why'] = 'flaky' if 0 < t['passes'] < t['n'] else 'always' if t['passes'] == t['n'] else 'never'
        bins = {b: round_robin([t for t in pool if t['why'] == b], rng) for b in ('flaky', 'never', 'always')}
        bins['never'] = [t for t in bins['never'] if t['teacher'] == 'kept']
        # no flaky left after v1: alternate never/always so a block can show gains and losses
        alt = [t for pair in zip(bins['never'], bins['always']) for t in pair]
        rest = bins['never'][len(alt) // 2:] + bins['always'][len(alt) // 2:]
        take = (bins['flaky'] + alt + rest)[:max(need, 0)]
        picked += take
        report[blk] = {'need': need, 'pool': len(pool), 'picked': len(take),
                       **{b: sum(1 for t in take if t['why'] == b) for b in bins}}
        print(blk, report[blk])
    Path(a.out).write_text(json.dumps({'version': 'v1-fill', 'runs': a.runs, 'target': a.target, 'report': report,
                                       'tasks': sorted(picked, key=lambda t: (t['block'], t['id']))},
                                      ensure_ascii=False, indent=1))
    print(f'wrote {a.out}: {len(picked)} tasks')
    if a.copy:
        dst = Path(a.copy)
        shutil.rmtree(dst, ignore_errors=True)
        dst.mkdir(parents=True)
        for t in picked:
            shutil.copytree(Path(a.tasks) / t['id'], dst / t['id'])


if __name__ == '__main__':
    main()
