#!/usr/bin/env python3
"""Per-task comparison of Harbor job dirs (`harbor run ... -o runs/<name>`).

    python3 runner/report.py runs/A runs/B [runs/C ...] [--md out.md]

Prints what identifies each run (checkpoint, plugin commit, DSH version, eval
commit) and a task-by-task reward table; tasks whose reward differs between
runs are marked, and a task whose content hash changed between runs is
flagged so a changed task is not read as a model change.
"""
import argparse
import json
from pathlib import Path


def load(job_dir: Path):
    """A Harbor job directory: one trial dir per attempt; tasks with several
    attempts (harbor run -k N) get their mean reward."""
    cfg = json.loads((job_dir / 'config.json').read_text())
    agent = (cfg.get('agents') or [{}])[0]
    kw = agent.get('kwargs', {})
    trials = [json.loads(p.read_text()) for p in sorted(job_dir.glob('*/result.json'))]
    version = next((t['agent_info'].get('version') for t in trials if t.get('agent_info')), '') or ''
    parts = dict(x.strip().split(' ', 1) for x in version.split(';') if ' ' in x.strip())
    by_task = {}
    for t in trials:
        tid = t['task_name'].split('/')[-1]
        reward = ((t.get('verifier_result') or {}).get('rewards') or {}).get('reward', 0.0)
        by_task.setdefault(tid, []).append((reward, t))
    rows = {}
    for tid, items in by_task.items():
        rewards = [r for r, _ in items]
        rows[tid] = {'id': tid, 'reward': sum(rewards) / len(rewards), 'n': len(rewards),
                     'task_hash': str(items[0][1].get('task_checksum', '')),
                     'status': ','.join(sorted({(t.get('exception_info') or {}).get('exception_type', 'ok')
                                                for _, t in items}))}
    score = sum(r['reward'] for r in rows.values())
    meta = {'name': job_dir.name, 'score': score, 'tasks': len(rows),
            'agent': {'checkpoint': {'model': kw.get('rwkv_model', agent.get('model_name') or agent.get('name')),
                                     'base_url': kw.get('rwkv_url', '-'), 'adapter': kw.get('adapter')},
                      'plugin_commit': parts.get('plugin', '-'), 'dsh_version': parts.get('dsh', '-')},
            'eval_commit': parts.get('eval', '-')}
    return meta, rows


def ident(meta):
    ag = meta.get('agent', {})
    ck = ag.get('checkpoint', {})
    return {
        'run': meta['name'],
        'checkpoint': f"{ck.get('model', '-')}" + (f"+{ck['adapter']}" if ck.get('adapter') else ''),
        'endpoint': ck.get('base_url', '-'),
        'plugin': ag.get('plugin_commit') or '-',
        'dsh': ag.get('dsh_version', '-'),
        'eval': meta.get('eval_commit') or '-',
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
        rewards = [f"{c['reward']:.2g}" if c else '—' for c in cells]
        notes = []
        if len({r for r in rewards if r != '—'}) > 1:
            notes.append('**changed**')
            flips += 1
        if len({c.get('task_hash') for c in cells if c}) > 1:
            notes.append('task edited')
        lines.append(f'| {tid} | ' + ' | '.join(rewards) + f" | {' '.join(notes)} |")
    lines.append(f'\n{flips} of {len(ids)} tasks changed reward.')
    text = '\n'.join(lines)
    print(text)
    if a.md:
        Path(a.md).write_text(text + '\n')


if __name__ == '__main__':
    main()
