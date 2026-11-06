"""Verifier for tasks converted from the pipeline banks (bank/convert.py).

A port of rwkv-agent-pipeline scripts/judge.ts (itself from RWKV-Agent
scoring.go), so a task is judged here exactly as the teacher's run was judged
when the training data was made. Reads, inside the task container:

  /tests/expect.json        {"turns": [TurnExpect|null...], "case": CaseExpect, "initial": {path: text}}
  /logs/agent/events-N.jsonl, final-N.txt, ws-N.json   written per turn by the backend
  /app                      the workspace after the last turn

One deliberate difference from judge.ts: `equals` ignores CRLF vs LF.

Writes /logs/verifier/reward.txt (1 or 0) and details.json (every failed
check, per turn), which diagnose/report use for attribution.

    python3 judge.py [--expect E] [--logs DIR] [--app DIR] [--out DIR]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

OLD_TO_DSH = {
    'read_file': ['read'], 'read_lines': ['read'], 'search_text': ['grep'], 'list_files': ['glob'],
    'replace_lines': ['edit', 'write'], 'append_file': ['edit', 'write'], 'write_file': ['write', 'edit'],
}
OLD_DISCOVERY = {'list_files', 'search_text', 'read_file', 'read_lines', 'bash'}
DSH_DISCOVERY = {'read', 'grep', 'glob', 'bash'}
WRITES = {'write', 'edit', 'write_file', 'edit_file'}


def dsh_names(old):
    return OLD_TO_DSH.get(old, [old])


def fold(text):
    return re.sub('[A-Z]', lambda m: m.group().lower(), text.replace('**', ''))


def is_han(c):
    o = ord(c)
    return (0x3400 <= o <= 0x4DBF or 0x4E00 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF
            or 0x20000 <= o <= 0x3134F)


def is_word(c):
    return c.isalnum() and not is_han(c)


def contains_token(output, want):
    if want == '':
        return True
    start = 0
    while True:
        at = output.find(want, start)
        if at < 0:
            return False
        before, after = output[:at], output[at + len(want):]
        ok = True
        if before:
            b1 = before[-1]
            if is_word(b1) and is_word(want[0]):
                ok = False
            if len(before) > 1 and b1 in '.,' and before[-2].isdigit():
                ok = False
        if after:
            a1 = after[0]
            if is_word(a1) and is_word(want[-1]):
                ok = False
            if len(after) > 1 and a1 in '.,' and after[1].isdigit() and want[-1].isdigit():
                ok = False
        if ok:
            return True
        start = at + 1


FIGURE = re.compile(r'[$€£¥]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?')


def number_in_text(text, want, tol):
    for m in FIGURE.finditer(text):
        value = float(re.sub(r'^[$€£¥]', '', m.group()).replace(',', ''))
        before = text[:m.start()]
        if re.search(r'[-−]$', before) and not re.search(r'\d[-−]$', before):
            value = -value
        if abs(value - want) <= tol:
            return True
    return False


def normalize_answer(text):
    t = text.strip()
    for marker in ('**', '__', '`', '*', '_'):
        if len(t) > 2 * len(marker) and t.startswith(marker) and t.endswith(marker):
            t = t[len(marker):-len(marker)].strip()
    return re.sub(r'[.。!！;；,，]+$', '', t).strip().lower()


def crlf(text):
    return text.replace('\r\n', '\n')


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def check_turn(exp, tools, output, ws, initial):
    f = []
    used = set(tools)
    if exp.get('unchanged_files'):
        writes = sorted(used & WRITES)
        if writes:
            f.append(f'read-only turn used {", ".join(writes)}')
    for old in exp.get('required_tools') or []:
        # viewing tools stand in for each other, under old (training bank) and DSH names alike
        ok = any(n in used for n in dsh_names(old)) or (old in OLD_DISCOVERY | DSH_DISCOVERY and used & DSH_DISCOVERY)
        if not ok:
            f.append(f'required tool {old} not called')
    for old in exp.get('forbidden_tools') or []:
        if any(n in used for n in dsh_names(old)):
            f.append(f'forbidden tool {old} called')
    if exp.get('require_active_no_call') and tools:
        f.append(f'tool calls in a no-call turn: {",".join(tools)}')
    fo = fold(output)
    for want in exp.get('output_contains') or []:
        hit = contains_token(fo, fold(want)) if exp.get('output_contains_token') else fold(want) in fo
        if not hit:
            f.append(f'output lacks {json.dumps(want, ensure_ascii=False)}')
    any_ = exp.get('output_contains_any') or []
    if any_ and not any((contains_token(fo, fold(w)) if exp.get('output_contains_any_token') else fold(w) in fo)
                        for w in any_):
        f.append(f'output lacks any of {json.dumps(any_, ensure_ascii=False)}')
    for bad in exp.get('output_excludes') or []:
        if bad in output.replace('**', ''):
            f.append(f'output contains {json.dumps(bad, ensure_ascii=False)}')
    if exp.get('max_output_chars') and len(output) > exp['max_output_chars']:
        f.append(f'output longer than {exp["max_output_chars"]}')
    if exp.get('expected_number') is not None:
        tol = exp.get('tolerance') or 0
        want = exp['expected_number']
        ok = (number_in_text(output, want, tol) if exp.get('expected_number_in_text')
              else len(output.strip()) <= 40 and number_in_text(output, want, tol))
        if not ok:
            f.append(f'no figure {want}±{tol}' + ('' if exp.get('expected_number_in_text') else ' as a bare value'))
    if exp.get('output_equals') is not None and normalize_answer(output) != normalize_answer(exp['output_equals']):
        f.append('output_equals')
    if exp.get('output_equals_any') and not any(normalize_answer(output) == normalize_answer(w)
                                                for w in exp['output_equals_any']):
        f.append('output_equals_any')
    for path in exp.get('unchanged_files') or []:
        if path not in initial:
            f.append(f'cannot verify read-only file: {path}')
        elif ws is None:
            f.append(f'no workspace snapshot for this turn: {path}')
        elif ws.get(path) != sha(initial[path]):
            f.append(f'read-only turn changed {path}')
    return f


def run_checks(checks, app, initial):
    f = []
    for c in checks:
        argv = c.get('argv') or []
        if not argv or argv[0] not in ('python3', 'node') or not c.get('protected_files'):
            f.append('invalid program check: executable or protected tests missing')
            continue
        tmp = Path(tempfile.mkdtemp(prefix='rae-check-'))
        try:
            proj = tmp / 'project'
            shutil.copytree(app, proj, symlinks=True,
                            ignore=shutil.ignore_patterns('__pycache__', 'node_modules', '*.pyc'))
            for p in c['protected_files']:
                if p.startswith('/') or '..' in p.split('/') or p not in initial:
                    raise ValueError(f'invalid protected test path: {p}')
                dest = proj / p
                if dest.is_symlink():
                    dest.unlink()
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(initial[p])
            env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
            timeout = min(c.get('timeout_ms') or 30000, 60000) / 1000
            r = subprocess.run(argv, cwd=proj, env=env, capture_output=True, text=True, timeout=timeout)
            if r.returncode != 0:
                f.append(f'program check failed ({" ".join(argv)}): {(r.stderr or r.stdout)[-2000:]}')
        except subprocess.TimeoutExpired:
            f.append(f'program check timed out ({" ".join(argv)})')
        except Exception as e:  # noqa: BLE001 - every failure is a failed check
            f.append(f'program check error: {e}')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return f


def check_case(exp, app, initial, all_tools):
    f = []
    for path, want in (exp.get('files') or {}).items():
        file = app / path
        if want.get('absent'):
            if file.exists():
                f.append(f'{path} should be absent')
            continue
        if not file.exists():
            f.append(f'{path} missing')
            continue
        text = file.read_bytes().decode('utf-8', errors='replace')  # exact bytes, no newline translation
        if want.get('unchanged') and text != initial.get(path):
            f.append(f'{path} changed')
        # Deliberately looser than judge.ts: CRLF vs LF is not a content error
        # (Python's csv module writes CRLF by default).
        if want.get('equals') is not None and crlf(text).rstrip() != crlf(want['equals']).rstrip():
            f.append(f'{path} differs from expected')
        for piece in want.get('contains') or []:
            if piece not in text:
                f.append(f'{path} lacks {json.dumps(piece, ensure_ascii=False)}')
    for old, mx in (exp.get('max_calls') or {}).items():
        names = set(dsh_names(old))
        n = sum(1 for t in all_tools if t in names)
        if n > mx:
            f.append(f'{old} called {n} times (max {mx})')
    f += run_checks(exp.get('checks') or [], app, initial)
    return f


def turn_tools(path):
    tools = []
    if path.exists():
        for line in path.read_text(errors='replace').splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get('type') == 'tool_call' and e.get('tool'):
                tools.append(e['tool'])
    return tools


def judge(expect, logs, app):
    initial = expect.get('initial') or {}
    details = {'turns': [], 'case': []}
    all_tools = []
    for n, exp in enumerate(expect.get('turns') or [], 1):
        ev = logs / f'events-{n}.jsonl'
        tools = turn_tools(ev)
        all_tools += tools
        fails = []
        if not ev.exists():
            fails.append('turn not run')
        elif exp:
            final = logs / f'final-{n}.txt'
            output = final.read_text(errors='replace') if final.exists() else ''
            wsf = logs / f'ws-{n}.json'
            ws = json.loads(wsf.read_text()) if wsf.exists() else None
            fails = check_turn(exp, tools, output, ws, initial)
        details['turns'].append({'turn': n, 'tools': tools, 'failures': fails})
    details['case'] = check_case(expect.get('case') or {}, app, initial, all_tools)
    ok = not details['case'] and all(not t['failures'] for t in details['turns'])
    return ok, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--expect', default='/tests/expect.json')
    ap.add_argument('--logs', default='/logs/agent')
    ap.add_argument('--app', default='/app')
    ap.add_argument('--out', default='/logs/verifier')
    a = ap.parse_args()
    ok, details = judge(json.loads(Path(a.expect).read_text()), Path(a.logs), Path(a.app))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'details.json').write_text(json.dumps(details, ensure_ascii=False, indent=1))
    (out / 'reward.txt').write_text('1\n' if ok else '0\n')
    print('PASS' if ok else 'FAIL', json.dumps(details, ensure_ascii=False)[:3000])


if __name__ == '__main__':
    main()
