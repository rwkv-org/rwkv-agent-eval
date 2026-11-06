#!/usr/bin/env python3
"""Check bank/judge.py against the pipeline's own verdicts on teacher runs.

For every teacher trajectory under rwkv-agent-pipeline/runs/<batch>/traj/,
re-judge its scripted turns and final workspace with judge.py and compare
with the failures result.json recorded. Failures the port cannot see are
ignored: turn-end reasons, live-source evidence, and per-turn read-only file
checks (the trajectory keeps only the final workspace).

    python3 bank/validate_judge.py [--limit N]
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402
from convert import PIPE, load_cases  # noqa: E402

IGNORED = ('turn ended', 'live source', 'read-only turn changed', 'cannot verify read-only',
           'no workspace snapshot', 'program check')


def relevant(fails):
    return sorted(f for f in fails if not f.startswith(IGNORED))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    cases = load_cases()
    n = agree = 0
    bad = []
    for res in sorted(PIPE.glob('overnight-20261106*/traj/*/result.json')):
        r = json.loads(res.read_text())
        if r['case'] not in cases:
            continue
        _, c = cases[r['case']]
        if c.get('web_mode') == 'real' or c.get('expect', {}).get('checks'):
            continue  # live web / program checks are not re-runnable from the record
        if len(r['turns']) != len([x for x in r['turns'] if x.get('scripted')]):
            continue  # simulated turns ran after the script and may have changed the workspace
        t = res.parent
        scripted = [x for x in r['turns'] if x.get('scripted')]
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp)
            for i, turn in enumerate(scripted, 1):
                ev = t / f'events-{i}.jsonl'
                (logs / f'events-{i}.jsonl').write_text(ev.read_text() if ev.exists() else '')
                (logs / f'final-{i}.txt').write_text(turn.get('final') or '')
            expect = {'turns': [x.get('expect') for x in c['turns']], 'case': c.get('expect') or {},
                      'initial': c.get('files') or {}}
            _, details = judge.judge(expect, logs, t / 'workspace')
        mine = relevant([f for x in details['turns'] for f in x['failures']] + details['case'])
        theirs = relevant([f for x in scripted for f in x.get('failures') or []] + (r.get('caseFailures') or []))
        n += 1
        if (not mine) == (not theirs):
            agree += 1
        else:
            bad.append((r['trajectory'], mine, theirs))
        if a.limit and n >= a.limit:
            break
    print(f'{agree}/{n} trajectories agree on pass/fail')
    for tid, mine, theirs in bad[:30]:
        print(f'  {tid}\n    judge.py: {mine}\n    pipeline: {theirs}')


if __name__ == '__main__':
    main()
