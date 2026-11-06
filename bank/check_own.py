#!/usr/bin/env python3
"""Self-check for hand-made bank cases (bank/own/cases/*.json, see bank/own/SPEC.md).

Every case must:
  - parse and follow the schema (id, category from the training domains, turns
    with prompt + expect, a reference for every turn);
  - PASS judge.py when the reference replies, tool calls and file edits are replayed;
  - FAIL judge.py for an agent that does nothing (empty replies, no tools);
  - not reuse a prompt from the training banks (normalized first-80-char match).

    python3 bank/check_own.py [bank/own/cases/x.json ...]     # default: all
Exit 1 if any case fails; prints one line per case.
"""
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402
import web_tool  # noqa: E402
from convert import BLOCKS, load_cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OWN = ROOT / 'bank' / 'own' / 'cases'
ARCHIVE = ROOT / 'bank' / 'web-archive'
TOOLS = {'bash', 'read', 'write', 'edit', 'glob', 'grep', 'web_search', 'web_fetch'}


def norm(s):
    return re.sub(r'\s+', '', s)[:80]


def replay(case, turns_ref, use_reference):
    """Run judge.py on a simulated agent; returns (ok, details)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        app, logs = tmp / 'app', tmp / 'logs'
        logs.mkdir()
        for p, text in (case.get('files') or {}).items():
            (app / p).parent.mkdir(parents=True, exist_ok=True)
            (app / p).write_text(text)
        app.mkdir(exist_ok=True)
        for n, ref in enumerate(turns_ref, 1):
            ref = ref if use_reference else {}
            for p, text in (ref.get('files') or {}).items():
                f = app / p
                if text is None:
                    f.unlink(missing_ok=True)
                else:
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_text(text)
            (logs / f'events-{n}.jsonl').write_text(''.join(
                json.dumps({'type': 'tool_call', 'tool': t}) + '\n' for t in ref.get('tools') or []))
            (logs / f'final-{n}.txt').write_text(ref.get('final') or '')
            ws = {str(f.relative_to(app)): hashlib.sha256(f.read_bytes()).hexdigest()
                  for f in app.rglob('*') if f.is_file()}
            (logs / f'ws-{n}.json').write_text(json.dumps(ws))
        expect = {'turns': [t.get('expect') for t in case['turns']], 'case': case.get('expect') or {},
                  'initial': case.get('files') or {}}
        return judge.judge(expect, logs, app)


def norm_url(u):
    return u.split('#')[0].rstrip('/').replace('http://', 'https://', 1)


def check_web(c):
    """Web cases (web_mode "real"): the archive written by bank/web_tool.py must hold
    every declared URL (2xx) and, for search cases, at least one search; and each
    answer the judge looks for must appear in the archived text, so the case
    cannot be graded on a fact the agent was never shown (set
    provenance.answer_derived = true when the answer is computed from the pages)."""
    cat = c.get('category', '')
    is_web = cat.startswith('外部信息-')
    if c.get('web_mode') != 'real':
        return ['web cases need "web_mode": "real" and an archive (bank/web_tool.py)'] if is_web else []
    f = ARCHIVE / f"{c['id']}.json"
    if not f.exists():
        return [f'no archive {f.relative_to(ROOT)}: capture pages with bank/web_tool.py']
    arc = json.loads(f.read_text())
    errs = []
    got = {norm_url(p['url']) for p in arc.get('pages') or [] if 200 <= (p.get('status') or 0) < 300}
    for u in c.get('urls') or []:
        if norm_url(u) not in got:
            errs.append(f'declared url not archived with 2xx: {u}')
    searching = not cat.startswith('外部信息-真实网页')
    if searching and not arc.get('search'):
        errs.append('search case without an archived search (bank/web_tool.py search)')
    if not searching and not c.get('urls'):
        errs.append('real-web case must declare its urls')
    if (c.get('provenance') or {}).get('answer_derived'):
        return errs
    text = '\n'.join([web_tool.text_of(p) for p in arc.get('pages') or []] +
                     [f"{r['title']}\n{r['snippet']}" for s in arc.get('search') or [] for r in s['results']]).lower()
    text = re.sub(r'\s+', ' ', text)
    for t in c['turns']:
        e = t.get('expect') or {}
        if 'web_search' in (e.get('forbidden_tools') or []) or e.get('require_active_no_call'):
            continue  # a local-answer turn
        for item in e.get('output_contains') or []:
            if re.sub(r'\s+', ' ', item.lower()) not in text and item.lower() not in json.dumps(c.get('files') or {}, ensure_ascii=False).lower():
                errs.append(f'answer {item!r} is in neither the archived pages nor the files')
        anyof = e.get('output_contains_any') or []
        blob = text + json.dumps(c.get('files') or {}, ensure_ascii=False).lower()
        if anyof and not any(re.sub(r'\s+', ' ', x.lower()) in blob for x in anyof):
            errs.append(f'no form of answer {anyof[:3]} is in the archived pages or files')
    return errs


def check(path, bank_prompts):
    errs = []
    try:
        c = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f'bad JSON: {e}']
    if c.get('id') != path.stem:
        errs.append('id must equal the file name')
    if not any(c.get('category', '').startswith(p) for p, _ in BLOCKS):
        errs.append(f'unknown category {c.get("category")!r}')
    turns = c.get('turns') or []
    if not turns or not all(isinstance(t.get('prompt'), str) and t['prompt'].strip() for t in turns):
        errs.append('every turn needs a prompt')
    if any(not (t.get('expect') or {}) for t in turns) and not (c.get('expect') or {}):
        errs.append('a turn without expect needs a case-level expect')
    refs = (c.get('reference') or {}).get('turns') or []
    if len(refs) != len(turns):
        errs.append('reference.turns must have one entry per turn')
    for r in refs:
        bad = set(r.get('tools') or []) - TOOLS
        if bad:
            errs.append(f'reference uses tools DSH does not have: {sorted(bad)}')
    if errs:
        return errs
    for t in turns:
        other = bank_prompts.get(norm(t['prompt']))
        if other and other != c['id']:
            errs.append(f'prompt reuses bank case {other}')
    errs += check_web(c)
    ok, details = replay(c, refs, True)
    if not ok:
        errs.append('reference does not pass: ' + json.dumps(details, ensure_ascii=False)[:800])
    ok, _ = replay(c, refs, False)
    if ok:
        errs.append('an agent that does nothing passes')
    return errs


def main():
    paths = [Path(p) for p in sys.argv[1:]] or sorted(OWN.glob('*.json'))
    bank_prompts = {norm(t['prompt']): cid for cid, (_, c) in load_cases().items() for t in c.get('turns') or []}
    failed = 0
    for p in paths:
        errs = check(p, bank_prompts)
        print(f'{"OK  " if not errs else "FAIL"} {p.stem}' + ('' if not errs else ': ' + ' | '.join(errs)))
        failed += bool(errs)
    print(f'{len(paths) - failed}/{len(paths)} cases pass the self-check')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
