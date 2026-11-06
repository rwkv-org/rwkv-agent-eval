#!/usr/bin/env python3
"""Search and fetch real web pages while writing a case, archiving exactly what was seen.

    python3 bank/web_tool.py search <case-id> "query" --match kw1 kw2 ... [--count 6]
    python3 bank/web_tool.py fetch  <case-id> <url> [--grep REGEX] [--show N]
    python3 bank/web_tool.py show   <case-id>

Everything lands in bank/web-archive/<case-id>.json, which bank/convert.py ships
as /rae/web.json and backends/dsh/web-replay.mjs replays:

  search  calls the DeepSeek Search API (key: DS_key in ~/.deepseek_api.sh) and
          stores {query, match, results: [{url, title, snippet, publishedAt}]}.
          At eval time the agent's web_search query is matched against `match`
          (case-insensitive substrings; the entry with most hits wins; no hit =
          no results), so list every keyword a reasonable query would contain,
          in Chinese and English. Any search sets search_mode = "replay".
  fetch   gets the page with curl (same User-Agent and flags as the training
          pipeline's real-web fetch, through the proxy); if curl does not get a
          2xx with a body, the DeepSeek Fetch API's Markdown is stored instead.
          Prints the page as plain text (what the agent will roughly read):
          the first --show characters, or only lines matching --grep.
A case with fetches only keeps search_mode = "unavailable" (web_search fails
with "open the URL from the task", as in the real-web training cases).
"""
import argparse
import datetime as dt
import fcntl
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'bank' / 'web-archive'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
META = '\n__FETCH_META__'
MAX_CHARS = 200_000
PROXY = os.environ.get('RAE_PROXY', 'http://127.0.0.1:2080')
API = 'https://api.deepseek.com/v1/tools/'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def key():
    text = (Path.home() / '.deepseek_api.sh').read_text()
    m = re.search(r'DS_key\s*=\s*["\']?([^"\'\s]+)', text)
    if not m:
        sys.exit('DS_key not found in ~/.deepseek_api.sh')
    return m.group(1)


def api(tool, body):
    req = urllib.request.Request(API + tool, json.dumps(body).encode(),
                                 {'Authorization': f'Bearer {key()}', 'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': PROXY, 'http': PROXY}))
    with opener.open(req, timeout=60) as r:
        return json.load(r)


def load(cid):
    f = OUT / f'{cid}.json'
    if f.exists():
        return json.loads(f.read_text())
    return {'case': cid, 'search_mode': 'unavailable', 'sources': [], 'complete': True, 'pages': [], 'search': []}


def save(arc):
    OUT.mkdir(exist_ok=True)
    (OUT / f"{arc['case']}.json").write_text(json.dumps(arc, ensure_ascii=False))


def text_of(page):
    body = page['body']
    if 'html' in (page.get('contentType') or '') or body.lstrip()[:15].lower().startswith(('<!doctype', '<html')):
        body = re.sub(r'(?is)<(script|style|noscript|svg)\b.*?</\1>', ' ', body)
        body = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h\d|tr|pre|section|article)>', '\n', body)
        body = html.unescape(re.sub(r'<[^>]+>', ' ', body))
    body = re.sub(r'[ \t\r\f\v]+', ' ', body)
    return re.sub(r'\n\s*\n+', '\n', body).strip()


def curl(url):
    r = subprocess.run(['curl', '-sS', '-L', '--max-time', '30', '-A', UA, '-x', PROXY,
                        '-w', f'{META}%{{http_code}}|%{{content_type}}|%{{url_effective}}', url],
                       capture_output=True, timeout=45)
    out = r.stdout.decode('utf-8', errors='replace')
    at = out.rfind(META)
    body, meta = (out[:at], out[at + len(META):]) if at >= 0 else (out, '')
    status, ctype, final = (meta.split('|') + ['', '', url])[:3]
    return {'url': url, 'finalUrl': final or url, 'at': now(), 'status': int(status or 0), 'contentType': ctype,
            'bytes': len(body[:MAX_CHARS]), 'body': body[:MAX_CHARS], 'captured_by': 'web_tool.py curl'}


def do_fetch(a):
    arc = load(a.case)
    norm = a.url.split('#')[0].rstrip('/')
    page = next((p for p in arc['pages'] if p['url'].split('#')[0].rstrip('/') == norm), None)
    if page is None:
        page = curl(a.url)
        if not (200 <= page['status'] < 300 and len(text_of(page)) > 200):
            try:
                r = api('fetch', {'url': a.url})
                md = (f"# {r.get('title')}\n\n" if r.get('title') else '') + (r.get('content') or '')
                page = {'url': a.url, 'finalUrl': a.url, 'at': now(), 'status': 200,
                        'contentType': 'text/markdown; charset=utf-8', 'bytes': len(md[:MAX_CHARS]),
                        'body': md[:MAX_CHARS], 'captured_by': 'web_tool.py deepseek-fetch'}
            except Exception as e:  # noqa: BLE001
                sys.exit(f'fetch failed: curl status {page["status"]}; DeepSeek fetch: {e}. Pick another URL.')
        arc['pages'].append(page)
        arc['sources'].append(f"{page['captured_by']} {page['at']}")
        save(arc)
    text = text_of(page)
    print(f"[{page['status']} {page['contentType']}] {page['finalUrl']}  ({len(text)} chars of text)")
    if a.grep:
        rx = re.compile(a.grep, re.I)
        pos = 0
        for line in text.splitlines():
            if rx.search(line):
                print(f'@{pos}: {line[:400]}')
            pos += len(line) + 1
    else:
        print(text[:a.show])


def do_search(a):
    if not a.match:
        sys.exit('--match is required: the keywords an agent query must contain to get these results')
    r = api('search', {'query': a.query, 'count': a.count})
    results = [{'url': x['url'], 'title': x.get('title') or '', 'snippet': x.get('summary') or x.get('snippet') or '',
                **({'publishedAt': x['date']} if x.get('date') else {})} for x in r.get('results') or []]
    if not results:
        sys.exit('no results; try another query')
    arc = load(a.case)
    arc['search_mode'] = 'replay'
    arc.setdefault('search', []).append({'query': a.query, 'match': a.match, 'at': now(), 'results': results})
    arc['sources'].append(f'deepseek-search {now()}')
    save(arc)
    for i, x in enumerate(results):
        print(f"[{i}] {x['title']}\n    {x['url']}  {x.get('publishedAt') or ''}\n    {x['snippet'][:500]}")


def do_show(a):
    arc = load(a.case)
    print(f"search_mode {arc['search_mode']}")
    for s in arc.get('search') or []:
        print(f"search {s['query']!r} match={s['match']} -> {len(s['results'])} results")
    for p in arc['pages']:
        print(f"page {p['status']} {p['url']} ({p['bytes']} bytes, {p.get('captured_by')})")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('search')
    s.add_argument('case'); s.add_argument('query')
    s.add_argument('--match', nargs='+', default=[]); s.add_argument('--count', type=int, default=6)
    f = sub.add_parser('fetch')
    f.add_argument('case'); f.add_argument('url')
    f.add_argument('--grep', default=''); f.add_argument('--show', type=int, default=6000)
    w = sub.add_parser('show')
    w.add_argument('case')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    with open(OUT / f'.{a.case}.lock', 'w') as lock:  # parallel calls on one case must not drop each other's writes
        fcntl.flock(lock, fcntl.LOCK_EX)
        {'search': do_search, 'fetch': do_fetch, 'show': do_show}[a.cmd](a)


if __name__ == '__main__':
    main()
