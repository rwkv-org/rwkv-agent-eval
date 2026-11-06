#!/usr/bin/env python3
"""Build the web archive for real-web bank cases: bank/web-archive/<case>.json.

Pages come from the teacher runs' snapshots.jsonl when the case was run (the
exact bytes the teacher saw, every URL it fetched); a declared URL with no 2xx
snapshot is fetched now with curl, the same way the pipeline's real-web.ts
does (same User-Agent, -L, 30 s). Existing archives are kept unless --force.

    python3 bank/capture_pages.py [--force] [--proxy http://127.0.0.1:2080] [ids...]
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert import PIPE, load_cases  # noqa: E402

OUT = Path(__file__).resolve().parent / 'web-archive'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
META = '\n__FETCH_META__'
MAX_CHARS = 200_000


PROXY = ''


def curl(url):
    r = subprocess.run(['curl', '-sS', '-L', '--max-time', '30', '-A', UA, *(['-x', PROXY] if PROXY else []),
                        '-w', f'{META}%{{http_code}}|%{{content_type}}|%{{url_effective}}', url],
                       capture_output=True, timeout=45)
    out = r.stdout.decode('utf-8', errors='replace')
    at = out.rfind(META)
    body, meta = (out[:at], out[at + len(META):]) if at >= 0 else (out, '')
    status, ctype, final = (meta.split('|') + ['', '', url])[:3]
    return {'url': url, 'finalUrl': final or url, 'at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': int(status or 0), 'contentType': ctype, 'bytes': len(body[:MAX_CHARS]),
            'body': body[:MAX_CHARS], 'captured_by': 'capture_pages.py'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--proxy', default='', help='e.g. http://127.0.0.1:2080 (what the pipeline used)')
    ap.add_argument('ids', nargs='*')
    a = ap.parse_args()
    global PROXY
    PROXY = a.proxy
    OUT.mkdir(exist_ok=True)
    cases = {k: c for k, (_, c) in load_cases().items() if c.get('web_mode') == 'real'}
    ids = a.ids or sorted(cases)
    for cid in ids:
        out = OUT / f'{cid}.json'
        if out.exists() and not a.force:
            continue
        c = cases[cid]
        pages, sources = [], []
        for snap in sorted(PIPE.glob(f'overnight-20261106*/traj/{cid}-t*/snapshots.jsonl')):
            sources.append(str(snap.relative_to(PIPE)))
            for line in snap.read_text().splitlines():
                try:
                    p = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not p.get('duplicate'):
                    pages.append(p)
        have = {p['url'].split('#')[0] for p in pages if 200 <= (p.get('status') or 0) < 300}
        for url in c.get('urls') or []:
            if url.split('#')[0] not in have:
                p = curl(url)
                pages.append(p)
                sources.append(f'curl {p["at"]}')
        ok = all(any(p['url'].split('#')[0] == u.split('#')[0] and 200 <= (p.get('status') or 0) < 300
                     for p in pages) for u in c.get('urls') or [])
        out.write_text(json.dumps({'case': cid, 'search_mode': 'unavailable', 'sources': sources,
                                   'complete': ok, 'pages': pages}, ensure_ascii=False))
        print(f'{cid}: {len(pages)} pages, declared urls {"ok" if ok else "MISSING"}, from {len(sources)} sources')


if __name__ == '__main__':
    main()
