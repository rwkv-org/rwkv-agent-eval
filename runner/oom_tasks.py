#!/usr/bin/env python3
"""Tasks whose trials hit the container memory cap, across one or more jobs.

    python3 runner/oom_tasks.py runs/eval-A/<job> [runs/eval-B/<job> ...] [--min 2]

Reads agent/turns.json `oom_kills` (processes the kernel killed at the cap,
written by backends/dsh/harbor_agent.py). Lists every task with an OOM trial:
trials with a kill / trials seen, and the kill count. Tasks at or above --min
trials with a kill are marked: candidates to check (does the reference
solution or the test need more than the cap?) before taking them out of the
bank. A single runaway trial is the model's failure, not the task's.
"""
import argparse
import collections
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs', nargs='+')
    ap.add_argument('--min', type=int, default=2, help='trials with a kill that mark a task (default 2)')
    a = ap.parse_args()
    seen, hit, kills = collections.Counter(), collections.Counter(), collections.Counter()
    unknown = 0
    for job in a.jobs:
        for result in Path(job).glob('*/result.json'):
            task = json.loads(result.read_text())['task_name'].split('/')[-1]
            seen[task] += 1
            try:
                n = json.loads((result.parent / 'agent' / 'turns.json').read_text()).get('oom_kills')
            except (OSError, json.JSONDecodeError):
                n = None
            if n is None:
                unknown += 1
            elif n > 0:
                hit[task] += 1
                kills[task] += n
    for task, n in sorted(hit.items(), key=lambda x: (-x[1], x[0])):
        mark = '  <- check' if n >= a.min else ''
        print(f'{task}\t{n}/{seen[task]} trials\t{kills[task]} kills{mark}')
    print(f'{len(hit)} tasks with an OOM trial; {sum(seen.values())} trials, {unknown} without an oom_kills record')


if __name__ == '__main__':
    main()
