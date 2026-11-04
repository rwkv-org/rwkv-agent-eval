#!/usr/bin/env python3
"""Per-task comparison of runs (workspace runner output).

    python3 runner/report.py runs/A runs/B [runs/C ...] [--md out.md]

Prints what identifies each run (checkpoint, plugin commit, DSH version, eval
commit) and a task-by-task reward table; tasks whose reward differs between
runs are marked, and a task whose content hash changed between runs is
flagged so a changed task is not read as a model change.
"""
import argparse
import json
from pathlib import Path


def load(run_dir: Path):
    meta = json.loads((run_dir / 'run.json').read_text())
    rows = {}
    for line in (run_dir / 'results.jsonl').read_text().splitlines():
        r = json.loads(line)
        rows[r['id']] = r
    return meta, rows


def ident(meta):
    ag = meta.get('agent', {})
    ck = ag.get('checkpoint', {})
    return {
        'run': meta['name'],
        'checkpoint': f"{ck.get('model', '-')}" + (f"+{ck['adapter']}" if ck.get('adapter') else ''),
        'endpoint': ck.get('base_url', '-'),
        'plugin': (ag.get('plugin_commit') or '-') + ('*' if ag.get('plugin_dirty') else ''),
        'dsh': ag.get('dsh_version', '-'),
        'eval': (meta.get('eval_commit') or '-') + ('*' if meta.get('eval_dirty') else ''),
        'score': f"{meta.get('score', 0):g}/{meta.get('tasks', 0)}",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--md', default='')
    a = ap.parse_args()
    runs = [load(Path(r)) for r in a.runs]

    lines = ['| | ' + ' | '.join(ident(m)['run'] for m, _ in runs) + ' |',
             '|---|' + '---|' * len(runs)]
    for key in ('checkpoint', 'endpoint', 'plugin', 'dsh', 'eval', 'score'):
        lines.append(f'| {key} | ' + ' | '.join(ident(m)[key] for m, _ in runs) + ' |')
    lines += ['', '| task | ' + ' | '.join(f'#{i + 1}' for i in range(len(runs))) + ' | note |',
              '|---|' + '---|' * (len(runs) + 1)]
    ids = sorted(set().union(*(rows.keys() for _, rows in runs)))
    flips = 0
    for tid in ids:
        cells = [rows.get(tid) for _, rows in runs]
        rewards = [f"{c['reward']:g}" if c else '—' for c in cells]
        notes = []
        if len({r for r in rewards if r != '—'}) > 1:
            notes.append('**changed**')
            flips += 1
        if len({c['task_hash'] for c in cells if c}) > 1:
            notes.append('task edited')
        lines.append(f'| {tid} | ' + ' | '.join(rewards) + f" | {' '.join(notes)} |")
    lines.append(f'\n{flips} of {len(ids)} tasks changed reward.')
    text = '\n'.join(lines)
    print(text)
    if a.md:
        Path(a.md).write_text(text + '\n')


if __name__ == '__main__':
    main()
