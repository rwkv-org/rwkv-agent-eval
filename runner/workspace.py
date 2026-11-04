#!/usr/bin/env python3
"""Run `environment = "workspace"` tasks (Harbor task format) without Docker.

    python3 runner/workspace.py --backend dsh --opt base_url=http://... --opt model=... \
        [--tasks tasks] [--ids a,b] [--jobs 4] [--name tag]
    python3 runner/workspace.py --oracle        # run solution/solve.sh: checks the tasks

Per task: copy environment/workspace/ to runs/<name>/ws/<task>/ (the agent's
cwd, nothing else in it), run the agent, then tests/test.sh in that directory
with RAE_TESTS_DIR / RAE_LOGS_DIR pointing at host paths. The reward is
logs/<task>/verifier/reward.txt. The agent's final message is saved as
logs/<task>/agent/final.txt, which answer tasks grade.
"""
import argparse
import concurrent.futures as cf
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    p = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ''


def task_hash(tdir: Path):
    h = hashlib.sha256()
    for f in sorted(p for p in tdir.rglob('*') if p.is_file()):
        h.update(str(f.relative_to(tdir)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def load_tasks(tasks_dir: Path, ids):
    out = []
    for toml_path in sorted(tasks_dir.glob('*/task.toml')):
        tdir = toml_path.parent
        cfg = tomllib.loads(toml_path.read_text())
        meta = cfg.get('metadata', {})
        if meta.get('environment', 'docker') != 'workspace':
            continue
        if ids and tdir.name not in ids:
            continue
        out.append({'id': tdir.name, 'dir': tdir, 'cfg': cfg, 'meta': meta})
    return out


def load_backend(name):
    path = ROOT / 'backends' / name / 'workspace.py'
    spec = importlib.util.spec_from_file_location(f'backend_{name}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_task(task, run_dir: Path, backend, opts, oracle):
    tid, tdir = task['id'], task['dir']
    ws, logs = run_dir / 'ws' / tid, run_dir / 'logs' / tid
    for d in (ws, logs):
        if d.exists():
            shutil.rmtree(d)
    (logs / 'agent').mkdir(parents=True)
    (logs / 'verifier').mkdir()
    seed = tdir / 'environment' / 'workspace'
    if seed.is_dir():
        shutil.copytree(seed, ws, ignore=shutil.ignore_patterns('.keep'))
    else:
        ws.mkdir(parents=True)
    env = dict(os.environ, RAE_TESTS_DIR=str(tdir / 'tests'), RAE_LOGS_DIR=str(logs))
    timeout = task['cfg'].get('agent', {}).get('timeout_sec') or 900

    if oracle:
        t0 = time.time()
        p = subprocess.run(['bash', str(tdir / 'solution' / 'solve.sh')], cwd=ws, env=env,
                           capture_output=True, text=True, timeout=timeout)
        res = {'final': '', 'status': 'ok' if p.returncode == 0 else f'exit {p.returncode}',
               'secs': round(time.time() - t0, 1)}
    else:
        instruction = (tdir / 'instruction.md').read_text()
        res = backend.run(instruction, ws, logs / 'agent', opts, timeout)
        (logs / 'agent' / 'final.txt').write_text(res['final'])

    vt = task['cfg'].get('verifier', {}).get('timeout_sec') or 120
    p = subprocess.run(['bash', str(tdir / 'tests' / 'test.sh')], cwd=ws, env=env,
                       capture_output=True, text=True, timeout=vt)
    (logs / 'verifier' / 'test-stdout.txt').write_text(p.stdout + p.stderr)
    reward_file = logs / 'verifier' / 'reward.txt'
    try:
        reward = float(reward_file.read_text().strip())
    except (OSError, ValueError):
        reward = 0.0
    detail = [l for l in (p.stdout + p.stderr).splitlines() if l.strip()][-3:]
    return dict(id=tid, reward=reward, detail=' | '.join(detail)[:300], task_hash=task_hash(tdir),
                role=task['meta'].get('role'), difficulty=task['meta'].get('difficulty'),
                **{k: v for k, v in res.items() if k != 'final'}, final=res['final'][:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tasks', default=str(ROOT / 'tasks'))
    ap.add_argument('--backend', default='dsh')
    ap.add_argument('--opt', action='append', default=[], help='backend option key=value')
    ap.add_argument('--ids', default='')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--name', default='')
    ap.add_argument('--oracle', action='store_true', help='run solution/solve.sh instead of an agent')
    a = ap.parse_args()

    # Docker task images default to UTC; match them so the same task sees the
    # same clock in both runners (agent, solution and verifier inherit this).
    os.environ['TZ'] = 'UTC'
    opts = dict(kv.split('=', 1) for kv in a.opt)
    tasks = load_tasks(Path(a.tasks), set(filter(None, a.ids.split(','))))
    backend = None if a.oracle else load_backend(a.backend)
    name = a.name or time.strftime('%Y%m%d-%H%M%S') + ('-oracle' if a.oracle else f'-{a.backend}')
    run_dir = ROOT / 'runs' / name
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        'name': name, 'runner': 'workspace', 'started': time.strftime('%F %T %z'),
        'eval_commit': git('rev-parse', '--short', 'HEAD'), 'eval_dirty': bool(git('status', '--porcelain')),
        'tasks': len(tasks),
        'agent': {'agent': 'oracle'} if a.oracle else backend.describe(opts),
    }
    (run_dir / 'run.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(json.dumps(meta, ensure_ascii=False), flush=True)

    results = []
    with cf.ThreadPoolExecutor(a.jobs) as pool, open(run_dir / 'results.jsonl', 'w') as rf:
        futs = [pool.submit(run_task, t, run_dir, backend, opts, a.oracle) for t in tasks]
        for fut in cf.as_completed(futs):
            r = fut.result()
            results.append(r)
            rf.write(json.dumps(r, ensure_ascii=False) + '\n')
            rf.flush()
            print(f"[{len(results)}/{len(tasks)}] reward={r['reward']:g} {r['id']} ({r['status']}, {r['secs']}s) "
                  f"{r['detail'][:100]}", flush=True)

    total = sum(r['reward'] for r in results)
    meta.update(finished=time.strftime('%F %T %z'), score=total, mean=round(total / max(1, len(results)), 3))
    (run_dir / 'run.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"score {total:g}/{len(results)}")


if __name__ == '__main__':
    sys.exit(main())
