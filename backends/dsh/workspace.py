"""DSH + dsh-rwkv-plugin backend for the workspace runner.

Runs one task through the plugin's headless entry (scripts/headless.ts) in the
task workspace. DSH's own sandbox policy (workspace-write) keeps writes inside
the workspace; there is no container.

Options (runner --opt key=value, or environment):
    base_url   RWKV endpoint                 (RAE_BASE_URL)
    model      upstream model id             (RAE_MODEL)
    backend    irwkv | lightning             (default irwkv)
    plugin     dsh-rwkv-plugin checkout      (RAE_PLUGIN, default ../dsh-rwkv-plugin)
    dsh_root   DSH source checkout, if DSH runs from source (DSH_ROOT)
    adapter, max_steps, thinking             passed through to headless.ts
"""
import json
import os
import subprocess
import time
from pathlib import Path

EVAL_ROOT = Path(__file__).resolve().parents[2]


def _opts(opts):
    o = dict(opts)
    o.setdefault('base_url', os.environ.get('RAE_BASE_URL', ''))
    o.setdefault('model', os.environ.get('RAE_MODEL', ''))
    o.setdefault('backend', 'irwkv')
    o.setdefault('plugin', os.environ.get('RAE_PLUGIN', str(EVAL_ROOT.parent / 'dsh-rwkv-plugin')))
    o.setdefault('dsh_root', os.environ.get('DSH_ROOT', ''))
    if not o['base_url'] or not o['model']:
        raise SystemExit('dsh backend needs base_url and model (--opt base_url=... --opt model=...)')
    return o


def _git(path, *args):
    p = subprocess.run(['git', '-C', str(path), *args], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ''


def describe(opts):
    """Everything that identifies this agent build, for run.json."""
    o = _opts(opts)
    info = {
        'agent': 'dsh+dsh-rwkv-plugin',
        'checkpoint': {'backend': o['backend'], 'base_url': o['base_url'], 'model': o['model'],
                       'adapter': o.get('adapter')},
        'plugin_commit': _git(o['plugin'], 'rev-parse', '--short', 'HEAD'),
        'plugin_dirty': bool(_git(o['plugin'], 'status', '--porcelain')),
        'harness': {k: o[k] for k in ('max_steps', 'thinking') if k in o},
    }
    if o['dsh_root']:
        info['dsh_version'] = 'source@' + _git(o['dsh_root'], 'rev-parse', '--short', 'HEAD')
    else:
        p = subprocess.run(['dsh', '--version'], capture_output=True, text=True)
        info['dsh_version'] = p.stdout.strip() or 'unknown'
    return info


def run(instruction, ws: Path, agent_logs: Path, opts, timeout):
    o = _opts(opts)
    cmd = ['node', str(Path(o['plugin']) / 'scripts/headless.ts'),
           '--backend', o['backend'], '--base-url', o['base_url'], '--model', o['model'],
           '--home', str(agent_logs / 'dsh-home')]
    for key in ('adapter', 'max_steps', 'thinking'):
        if key in o:
            cmd += ['--' + key.replace('_', '-'), str(o[key])]
    cmd.append('-')
    env = dict(os.environ)
    env.pop('DEEPSEEK_API_KEY', None)
    if o['dsh_root']:
        env['DSH_ROOT'] = o['dsh_root']
    t0, status = time.time(), 'ok'
    with open(agent_logs / 'events.jsonl', 'w') as out, open(agent_logs / 'stderr.txt', 'w') as err:
        try:
            p = subprocess.run(cmd, cwd=ws, env=env, input=instruction, text=True,
                               stdout=out, stderr=err, timeout=timeout)
            if p.returncode:
                status = f'exit {p.returncode}'
        except subprocess.TimeoutExpired:
            status = 'timeout'
    events = []
    for line in (agent_logs / 'events.jsonl').read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    final = next((e.get('text', '') for e in reversed(events) if e.get('type') == 'final'), '')
    usage = [e['usage'] for e in events if e.get('type') == 'status' and 'usage' in e]
    return {
        'final': final,
        'status': status,
        'secs': round(time.time() - t0, 1),
        'tool_calls': sum(1 for e in events if e.get('type') == 'tool_call'),
        'tool_errors': sum(1 for e in events if e.get('type') == 'tool_result' and e.get('status') == 'error'),
        'output_tokens': sum(u.get('outputTokens', 0) for u in usage),
    }
