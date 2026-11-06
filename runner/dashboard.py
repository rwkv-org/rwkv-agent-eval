#!/usr/bin/env python3
"""Score dashboard across runs: total and per eval block, with uncertainty.

    python3 runner/dashboard.py runs/A runs/B [...] [--tasks DIR] [--labels a,b] [--out dashboard.html]

Runs are Harbor job dirs (or their parent, `harbor run -o X`), in the order
to plot; the first is the baseline. Task metadata (block, split) comes from
task.toml under --tasks (default: build/candidates, then tasks/).

Statistics are task-level, because trials of one task are correlated: a
task's score is the mean of its trials; a block's score is the mean over its
tasks, ± 1.96 standard errors of those task means. A change against the
baseline is the mean per-task difference over tasks both runs scored, with a
paired standard error; |change| > 1.96 SE is marked as significant. Trials
that raised (environment errors) are left out and counted.
"""
import argparse
import html
import json
import math
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK_NAMES = {
    'direct': '直接回答', 'read-local': '查找阅读·本地', 'read-code': '查找阅读·代码', 'stat': '统计计算',
    'edit-data': '改文件·配置数据', 'edit-code': '改文件·代码混合', 'code-fix': '代码修复',
    'web-local': '网页+本地', 'web-code': '网页+代码', 'search': '搜索问答', 'env': '环境探针',
}


def trials_of(job):
    out = {}
    for f in list(job.glob('*/result.json')) + list(job.glob('*/*/result.json')):
        r = json.loads(f.read_text())
        if 'task_name' not in r:
            continue
        tid = r['task_name'].split('/')[-1]
        exc = (r.get('exception_info') or {}).get('exception_type')
        reward = ((r.get('verifier_result') or {}).get('rewards') or {}).get('reward')
        info = r.get('agent_info') or {}
        out.setdefault(tid, []).append((exc, float(reward or 0), info.get('version') or ''))
    return out


def identity(trials):
    version = next((v for ts in trials.values() for _, _, v in ts if v), '')
    return dict(x.strip().split(' ', 1) for x in version.split(';') if ' ' in x.strip())


def load_meta(dirs):
    meta = {}
    for d in dirs:
        for t in Path(d).glob('*/task.toml'):
            meta.setdefault(t.parent.name, tomllib.loads(t.read_text()).get('metadata', {}))
    return meta


def task_scores(trials):
    """task id -> mean reward over trials that did not raise; plus error count."""
    scores, errors = {}, 0
    for tid, ts in trials.items():
        ok = [r for exc, r, _ in ts if not exc]
        errors += len(ts) - len(ok)
        if ok:
            scores[tid] = sum(ok) / len(ok)
    return scores, errors


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return None, None
    m = sum(xs) / n
    if n < 2:
        return m, None
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def stats(runs, meta):
    blocks = sorted({meta.get(t, {}).get('block', '?') for r in runs for t in r['scores']},
                    key=lambda b: list(BLOCK_NAMES).index(b) if b in BLOCK_NAMES else 99)
    base = runs[0]['scores']
    rows = []
    for blk in ['ALL'] + blocks:
        row = {'block': blk, 'runs': []}
        for r in runs:
            ids = [t for t in r['scores'] if blk == 'ALL' or meta.get(t, {}).get('block') == blk]
            m, se = mean_se([r['scores'][t] for t in ids])
            common = [t for t in ids if t in base]
            dm, dse = mean_se([r['scores'][t] - base[t] for t in common])
            row['runs'].append({'n': len(ids), 'mean': m, 'se': se, 'delta': dm, 'delta_se': dse,
                                'paired': len(common)})
        rows.append(row)
    return rows


def split_grid(run, meta):
    cells = {}
    for t, s in run['scores'].items():
        m = meta.get(t, {})
        cells.setdefault((m.get('block', '?'), m.get('split', '?')), []).append(s)
    return {k: (sum(v) / len(v), len(v)) for k, v in cells.items()}


def pct(x):
    return '—' if x is None else f'{100 * x:.1f}%'


def signed(x):
    return '—' if x is None else f'{100 * x:+.1f}'


def significant(r):
    return r['delta'] is not None and r['delta_se'] and abs(r['delta']) > 1.96 * r['delta_se']


def panel(row, labels, w=300, h=170, big=False):
    """One block's score across runs: line + markers + 95% band, single series."""
    if big:
        w, h = 640, 220
    pl, pr, pt, pb = 40, 12, 14, 26
    pw, ph = w - pl - pr, h - pt - pb
    rs = row['runs']
    n = len(rs)
    x = (lambda i: pl + pw / 2) if n == 1 else (lambda i: pl + pw * i / (n - 1))
    y = lambda v: pt + ph * (1 - v)
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{html.escape(name(row["block"]))} 通过率">']
    for g in (0, .25, .5, .75, 1):
        parts.append(f'<line x1="{pl}" x2="{w - pr}" y1="{y(g):.1f}" y2="{y(g):.1f}" class="grid"/>'
                     f'<text x="{pl - 6}" y="{y(g) + 3.5:.1f}" class="tick" text-anchor="end">{int(g * 100)}</text>')
    pts = [(i, r) for i, r in enumerate(rs) if r['mean'] is not None]
    band = [(i, max(0, r['mean'] - 1.96 * r['se']), min(1, r['mean'] + 1.96 * r['se'])) for i, r in pts if r['se']]
    if len(band) >= 2:
        d = ' '.join(f'{x(i):.1f},{y(hi):.1f}' for i, _, hi in band) + ' ' + \
            ' '.join(f'{x(i):.1f},{y(lo):.1f}' for i, lo, _ in reversed(band))
        parts.append(f'<polygon points="{d}" class="band"/>')
    elif len(band) == 1:
        i, lo, hi = band[0]
        parts.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{y(lo):.1f}" y2="{y(hi):.1f}" class="whisker"/>')
    if len(pts) >= 2:
        parts.append('<polyline class="line" points="' + ' '.join(f'{x(i):.1f},{y(r["mean"]):.1f}' for i, r in pts) + '"/>')
    for i, r in pts:
        tip = (f'{labels[i]} · {name(row["block"])}<br>通过率 {pct(r["mean"])}'
               + (f' ± {100 * 1.96 * r["se"]:.1f}' if r['se'] else '') + f'（{r["n"]} 题）'
               + (f'<br>比基线 {signed(r["delta"])} 点' + (f' ± {100 * 1.96 * r["delta_se"]:.1f}' if r['delta_se'] else '')
                  + f'（配对 {r["paired"]} 题）' + ('，显著' if significant(r) else '') if i else ''))
        parts.append(f'<circle cx="{x(i):.1f}" cy="{y(r["mean"]):.1f}" r="4.5" class="dot{" sig" if i and significant(r) else ""}"/>'
                     f'<circle cx="{x(i):.1f}" cy="{y(r["mean"]):.1f}" r="14" class="hit" data-tip="{html.escape(tip)}"/>')
    last = pts[-1][1] if pts else None
    if last is not None and pts:
        i = pts[-1][0]
        parts.append(f'<text x="{min(x(i) + 8, w - pr - 2):.1f}" y="{y(last["mean"]) - 8:.1f}" class="value" '
                     f'text-anchor="{"end" if n > 1 else "start"}">{pct(last["mean"])}</text>')
    for i, lab in enumerate(labels):
        if n <= 8 or i in (0, n - 1):
            anchor = 'middle' if n == 1 else 'start' if i == 0 else 'end' if i == n - 1 else 'middle'
            parts.append(f'<text x="{x(i):.1f}" y="{h - 8}" class="tick" text-anchor="{anchor}">{html.escape(lab[:14])}</text>')
    parts.append('</svg>')
    last_run = rs[-1]
    delta = '' if len(rs) < 2 or last_run['delta'] is None else (
        f'<span class="delta{" sig" if significant(last_run) else ""}">{signed(last_run["delta"])} 点'
        f'{" ▲" if significant(last_run) and last_run["delta"] > 0 else " ▼" if significant(last_run) else ""}</span>')
    return (f'<figure class="panel{" big" if big else ""}"><figcaption><b>{html.escape(name(row["block"]))}</b>'
            f'<span class="n">{last_run["n"]} 题</span>{delta}</figcaption>{"".join(parts)}</figure>')


def name(b):
    return '总分' if b == 'ALL' else BLOCK_NAMES.get(b, b)


SEQ = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5', '#2a78d6', '#256abf',
       '#1c5cab', '#184f95', '#104281', '#0d366b']


def heatmap(grid, blocks):
    splits = [s for s in ('seen', 'heldout') if any(k[1] == s for k in grid)]
    head = ''.join(f'<th>{"已训回测" if s == "seen" else "留出"}</th>' for s in splits)
    body = []
    for b in blocks:
        cells = []
        for s in splits:
            v = grid.get((b, s))
            if v is None:
                cells.append('<td class="empty">—</td>')
                continue
            m, n = v
            c = SEQ[min(len(SEQ) - 1, int(m * (len(SEQ) - 1) + .5))]
            ink = '#0b0b0b' if m < .55 else '#ffffff'
            cells.append(f'<td style="background:{c};color:{ink}" data-tip="{html.escape(name(b))} · '
                         f'{"已训回测" if s == "seen" else "留出"}<br>{pct(m)}（{n} 题）">{pct(m)}<small>{n}</small></td>')
        body.append(f'<tr><th>{html.escape(name(b))}</th>{"".join(cells)}</tr>')
    return f'<table class="heat"><thead><tr><th></th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


CSS = '''
.viz-root{color-scheme:light;--surface-1:#fcfcfb;--surface-2:#f3f2ef;--text-primary:#0b0b0b;--text-secondary:#52514e;
--text-muted:#76756f;--grid:#e4e3df;--series-1:#2a78d6;--band:rgba(42,120,214,.16);--good:#0ca30c;--critical:#d03b3b}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;--surface-1:#1a1a19;
--surface-2:#242422;--text-primary:#f0efec;--text-secondary:#c3c2b7;--text-muted:#9a998f;--grid:#33332f;--series-1:#3987e5;
--band:rgba(57,135,229,.22)}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface-1:#1a1a19;--surface-2:#242422;--text-primary:#f0efec;
--text-secondary:#c3c2b7;--text-muted:#9a998f;--grid:#33332f;--series-1:#3987e5;--band:rgba(57,135,229,.22)}
body{margin:0;background:var(--surface-1)}
.viz-root{background:var(--surface-1);color:var(--text-primary);font:14px/1.45 system-ui,-apple-system,"PingFang SC",sans-serif;
padding:24px;max-width:1280px;margin:auto}
h1{font-size:20px;margin:0 0 4px}h2{font-size:15px;margin:28px 0 10px}.sub{color:var(--text-secondary);margin:0 0 16px}
table.ids{border-collapse:collapse;font-size:12.5px;margin-bottom:8px}table.ids td,table.ids th{padding:3px 10px;border-bottom:1px solid var(--grid);text-align:left}
table.ids th{color:var(--text-secondary);font-weight:500}code{font:12px ui-monospace,Menlo,monospace}
.grid-panels{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px}
.panel{margin:0;background:var(--surface-2);border-radius:10px;padding:10px 12px 4px}.panel.big{grid-column:1/-1;max-width:680px}
figcaption{display:flex;gap:10px;align-items:baseline;font-size:13.5px}figcaption .n{color:var(--text-muted);font-size:12px}
.delta{margin-left:auto;color:var(--text-secondary);font-size:12.5px;font-variant-numeric:tabular-nums}.delta.sig{color:var(--text-primary);font-weight:600}
svg .grid{stroke:var(--grid);stroke-width:1}svg .tick{fill:var(--text-muted);font-size:10.5px}
svg .line{fill:none;stroke:var(--series-1);stroke-width:2;stroke-linejoin:round}svg .band{fill:var(--band)}
svg .whisker{stroke:var(--series-1);stroke-width:2;opacity:.45}
svg .dot{fill:var(--series-1);stroke:var(--surface-2);stroke-width:2}svg .dot.sig{stroke:var(--text-primary);stroke-width:2}
svg .hit{fill:transparent;cursor:default}svg .value{fill:var(--text-primary);font-size:12px;font-weight:600}
table.heat{border-collapse:separate;border-spacing:2px;font-size:13px}table.heat th{font-weight:500;color:var(--text-secondary);padding:4px 10px;text-align:left}
table.heat td{min-width:96px;padding:7px 10px;border-radius:4px;font-variant-numeric:tabular-nums}table.heat td small{opacity:.75;margin-left:6px;font-size:11px}
table.heat td.empty{color:var(--text-muted);background:var(--surface-2)}
details{margin-top:24px}table.data{border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums}
table.data td,table.data th{padding:3px 10px;border-bottom:1px solid var(--grid);text-align:right}table.data th:first-child,table.data td:first-child{text-align:left}
#tip{position:fixed;pointer-events:none;background:var(--text-primary);color:var(--surface-1);font-size:12px;padding:6px 9px;border-radius:6px;
display:none;max-width:320px;z-index:9;line-height:1.4}
.note{color:var(--text-muted);font-size:12px;margin-top:8px}
'''

JS = '''
const tip=document.getElementById('tip');
document.addEventListener('mousemove',e=>{const t=e.target.closest('[data-tip]');
if(!t){tip.style.display='none';return}tip.innerHTML=t.dataset.tip;tip.style.display='block';
const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8),y=e.clientY+16+tip.offsetHeight>innerHeight?e.clientY-tip.offsetHeight-10:e.clientY+16;
tip.style.left=x+'px';tip.style.top=y+'px'});
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--tasks', action='append', default=[])
    ap.add_argument('--labels', default='')
    ap.add_argument('--out', default='dashboard.html')
    a = ap.parse_args()
    meta = load_meta(a.tasks or [ROOT / 'build' / 'candidates', ROOT / 'tasks'])
    runs = []
    for i, p in enumerate(a.runs):
        tr = trials_of(Path(p))
        scores, errors = task_scores(tr)
        runs.append({'path': p, 'scores': scores, 'errors': errors, 'id': identity(tr),
                     'trials': sum(len(v) for v in tr.values())})
    labels = a.labels.split(',') if a.labels else [Path(r['path'].rstrip('/')).name for r in runs]
    rows = stats(runs, meta)
    blocks = [r['block'] for r in rows[1:]]
    ids = ''.join(
        f'<tr><td>{html.escape(labels[i])}{"（基线）" if i == 0 else ""}</td><td><code>{html.escape(r["id"].get("model", "-"))}</code></td>'
        f'<td><code>{html.escape(r["id"].get("adapter", "-"))}</code></td><td><code>{html.escape(r["id"].get("dsh", "-"))}</code></td>'
        f'<td><code>{html.escape(r["id"].get("plugin", "-"))}</code></td><td><code>{html.escape(r["id"].get("eval", "-"))}</code></td>'
        f'<td>{r["trials"]}</td><td>{r["errors"]}</td></tr>' for i, r in enumerate(runs))
    data_rows = ''.join(
        f'<tr><td>{html.escape(name(row["block"]))}</td>' + ''.join(
            f'<td>{pct(r["mean"])}</td><td>{"" if r["se"] is None else f"±{100 * 1.96 * r["se"]:.1f}"}</td><td>{r["n"]}</td>'
            f'<td>{signed(r["delta"]) if i else ""}{"*" if i and significant(r) else ""}</td>'
            for i, r in enumerate(row['runs'])) + '</tr>' for row in rows)
    data_head = ''.join(f'<th colspan="4">{html.escape(l)}</th>' for l in labels)
    data_sub = '<th>通过率</th><th>95%</th><th>题数</th><th>比基线</th>' * len(runs)
    out = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RWKV Agent 评测看板</title><style>{CSS}</style></head><body><div class="viz-root">
<h1>RWKV Agent 评测看板</h1><p class="sub">{len(runs)} 次运行 · 题目层面统计（每题先取各次 trial 的平均） · 色带为 95% 区间 · 比基线为同题配对差，* / 描边点 = 显著</p>
<table class="ids"><tr><th>运行</th><th>模型</th><th>adapter</th><th>DSH</th><th>插件</th><th>eval</th><th>trial</th><th>环境报错</th></tr>{ids}</table>
<h2>总分与各能力块</h2><div class="grid-panels">{panel(rows[0], labels, big=True)}{"".join(panel(r, labels) for r in rows[1:])}</div>
<h2>{html.escape(labels[-1])}：能力块 × 是否训练过</h2>{heatmap(split_grid(runs[-1], meta), blocks)}
<p class="note">已训回测低、留出也低：没学会或框架问题；已训回测高、留出低：泛化不足；两者都高而开源题低：题面/任务形态覆盖不足。</p>
<details><summary>数据表</summary><table class="data"><thead><tr><th></th>{data_head}</tr><tr><th>能力块</th>{data_sub}</tr></thead>
<tbody>{data_rows}</tbody></table></details>
<div id="tip" role="tooltip"></div></div><script>{JS}</script></body></html>'''
    Path(a.out).write_text(out)
    print(f'wrote {a.out}')


if __name__ == '__main__':
    main()
