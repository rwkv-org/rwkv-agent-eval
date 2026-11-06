#!/usr/bin/env python3
"""Turn pipeline bank cases (rwkv-agent-pipeline runs/<bank>/cases/<id>.json)
into Harbor tasks graded by bank/judge.py.

    python3 bank/convert.py --ids ids.txt --out build/candidates      # ids: one per line, `#` comments
    python3 bank/convert.py --pool heldout --out build/candidates     # every eligible case not trained on

Each task records where it came from and how it relates to the training mix
([metadata] block / domain / split / origin_case), which report.py and the
dashboard use to group scores and trace a failure back to training rows.

Real-web cases ship their archive (bank/web-archive, bank/capture_pages.py) as
/rae/web.json, replayed by backends/dsh/web-replay.mjs. Skipped (reported):
cases with a hand-written web fixture (fictional pages), real-web cases whose
archive is missing or incomplete.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT.parent / 'rwkv-agent-pipeline' / 'runs'
BANKS = {'bank-1336': PIPE / 'bank-1336' / 'cases',
         'coding-expansion-bank': PIPE / 'coding-expansion-bank' / 'cases',
         'real-web-expansion-bank': PIPE / 'real-web-expansion-bank' / 'cases',
         'own': ROOT / 'bank' / 'own' / 'cases'}  # hand-made, never trained on (bank/own/SPEC.md)
MIX = PIPE / 'mix-20261106' / 'blocks' / 'Agent'
COVERAGE = PIPE / 'overnight-20261106' / 'full-coverage.jsonl'
FULL_INDEX = PIPE / 'overnight-20261106' / 'full-index.jsonl'

# Training domain (block file name in mix-20261106) -> eval capability block.
BLOCKS = [
    ('直接回答-', 'direct'),
    ('查找阅读-代码', 'read-code'),
    ('查找阅读-', 'read-local'),
    ('统计计算-', 'stat'),
    ('改文件写产物-代码', 'edit-code'),
    ('改文件写产物-跨类混合', 'edit-code'),
    ('改文件写产物-', 'edit-data'),
    ('代码任务-', 'code-fix'),
    ('外部信息-真实网页-Coding', 'web-code'),
    ('外部信息-真实网页-', 'web-local'),
    ('外部信息-', 'search'),
    ('终端操作-', 'terminal'),  # own cases only: shell work in one container (no training domain)
]
# Use Docker's default bridge instead of a compose network per trial: the
# default address pools hold ~31 networks, far below a high-concurrency run.
COMPOSE = '''services:
  main:
    network_mode: bridge
'''
SUB_BLOCKS = {'direct', 'read-code', 'read-local', 'stat', 'search'}  # graded mainly on the reply


def block_of(domain):
    return next(b for prefix, b in BLOCKS if domain.startswith(prefix))


def load_status():
    mix = set()
    for f in MIX.glob('*.jsonl'):
        for line in f.open():
            mix.add(json.loads(line)['meta']['case_id'])
    full = {json.loads(l)['case_id'] for l in FULL_INDEX.open()}
    cov = {}
    for line in COVERAGE.open():
        r = json.loads(line)
        cov[r['case_id']] = r
    return mix, full, cov


def teacher_status(cid, full, cov):
    if cid in full:
        return 'kept'
    if cid in cov:
        return 'failed' if cov[cid]['status'] == 'failed' else 'qc-dropped'
    return 'not-run'


def load_cases():
    cases = {}
    for bank, d in BANKS.items():
        for p in sorted(d.glob('*.json')) if d.is_dir() else []:
            c = json.loads(p.read_text())
            cases[c['id']] = (bank, c)
    return cases


ARCHIVE = ROOT / 'bank' / 'web-archive'


def web_archive(c):
    f = ARCHIVE / f"{c['id']}.json"
    return json.loads(f.read_text()) if f.exists() else None


def skip_reason(c):
    if c.get('web_mode') == 'real':
        arc = web_archive(c)
        if arc is None:
            return 'real-web without archive (run bank/capture_pages.py)'
        if not arc.get('complete'):
            return 'real-web archive misses a declared URL'
    if c.get('web_fixture'):
        return 'hand-written web fixture'
    if not c.get('turns'):
        return 'no turns'
    return ''


def toml_str(s):
    return json.dumps(str(s), ensure_ascii=False)


def write_task(out, bank, c, domain, split, teacher):
    d = out / c['id']
    if d.exists():
        shutil.rmtree(d)
    (d / 'environment' / 'workspace').mkdir(parents=True)
    (d / 'tests').mkdir()
    files = c.get('files') or {}
    for path, text in files.items():
        f = d / 'environment' / 'workspace' / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    if not files:
        (d / 'environment' / 'workspace' / '.keep').write_text('')
    prompts = [t['prompt'] for t in c['turns']]
    docker = ['FROM python:3.12-slim', 'WORKDIR /app', 'COPY workspace/ /app/']
    if len(prompts) > 1:
        (d / 'environment' / 'turns.json').write_text(json.dumps(prompts, ensure_ascii=False, indent=1))
        docker.append('COPY turns.json /rae/turns.json')
    arc = web_archive(c) if c.get('web_mode') == 'real' else None
    if arc is not None:
        (d / 'environment' / 'web.json').write_text(json.dumps(
            {'search_mode': arc['search_mode'], 'search': arc.get('search') or [], 'pages': arc['pages']}, ensure_ascii=False))
        docker.append('COPY web.json /rae/web.json')
    (d / 'environment' / 'Dockerfile').write_text('\n'.join(docker) + '\n')
    (d / 'environment' / 'docker-compose.yaml').write_text(COMPOSE)
    # .keep files and empty dirs: COPY of an empty workspace needs the dir to exist.
    (d / 'instruction.md').write_text(prompts[0].rstrip() + '\n')
    expect = {'turns': [t.get('expect') for t in c['turns']], 'case': c.get('expect') or {}, 'initial': files}
    (d / 'tests' / 'expect.json').write_text(json.dumps(expect, ensure_ascii=False, indent=1))
    shutil.copy(ROOT / 'bank' / 'judge.py', d / 'tests' / 'judge.py')
    (d / 'tests' / 'test.sh').write_text(
        '#!/usr/bin/env bash\n'
        '# Bank task: graded by judge.py (port of the pipeline judge) from per-turn logs and /app.\n'
        'export PATH=/opt/rae-node/bin:$PATH\n'
        'python3 /tests/judge.py\n')
    (d / 'tests' / 'test.sh').chmod(0o755)
    blk = block_of(domain)
    answer = any((t.get('expect') or {}).get(k) for t in c['turns'] for k in
                 ('output_contains', 'output_contains_any', 'expected_number', 'output_equals', 'output_equals_any'))
    turns = len(prompts)
    (d / 'task.toml').write_text(f'''schema_version = "1.4"

[task]
name = {toml_str('rwkv-agent-eval/' + c['id'])}
description = {toml_str(prompts[0][:120])}

[metadata]
role = {toml_str('sub' if blk in SUB_BLOCKS else 'main')}
difficulty = "uncalibrated"
source = {toml_str('pipeline:' + bank)}
category = {toml_str(domain)}
block = {toml_str(blk)}
split = {toml_str(split)}
origin_case = {toml_str(c['id'])}
teacher = {toml_str(teacher)}
turns = {turns}
answer = {'true' if answer else 'false'}

[agent]
timeout_sec = {min(300 * turns, 1500)}

[verifier]
timeout_sec = 180
environment_mode = "shared"
''')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', help='file with case ids, one per line')
    ap.add_argument('--pool', choices=['heldout', 'seen'], help='heldout: every eligible case not in the mix')
    ap.add_argument('--out', default=str(ROOT / 'build' / 'candidates'))
    ap.add_argument('--manifest', default='', help='write a JSONL manifest (one line per task) here')
    a = ap.parse_args()
    mix, full, cov = load_status()
    cases = load_cases()
    if a.ids:
        ids = [l.split('#')[0].strip() for l in Path(a.ids).read_text().splitlines()]
        ids = [i for i in ids if i]
    elif a.pool:
        ids = sorted(i for i in cases if (i in mix) == (a.pool == 'seen'))
    else:
        sys.exit('give --ids or --pool')
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    made, skipped, manifest = 0, {}, []
    for cid in ids:
        if cid not in cases:
            skipped.setdefault('unknown id', []).append(cid)
            continue
        bank, c = cases[cid]
        why = skip_reason(c)
        if why:
            skipped.setdefault(why, []).append(cid)
            continue
        domain = cov.get(cid, {}).get('domain') or c.get('category')
        split = 'seen' if cid in mix else 'heldout'
        teacher = teacher_status(cid, full, cov)
        write_task(out, bank, c, domain, split, teacher)
        manifest.append({'id': cid, 'bank': bank, 'domain': domain, 'block': block_of(domain), 'split': split,
                         'teacher': teacher, 'turns': len(c['turns'])})
        made += 1
    if a.manifest:
        Path(a.manifest).write_text(''.join(json.dumps(m, ensure_ascii=False) + '\n' for m in manifest))
    print(f'wrote {made} tasks to {out}')
    for why, xs in skipped.items():
        print(f'skipped {len(xs)}: {why}')


if __name__ == '__main__':
    main()
