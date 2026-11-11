"""Base model, literal vs hashline edit: adoption of the tag format, refusals, scores.

Usage (eval root): python3 experiments/edit-prompt/analyze_hashline.py runs/edit-hashline-base-<stamp>
In the hashline arm every edit that reaches a file was planned from LINE#ID tags;
a refused call reaches DSH with old_string = "\\u0000hashline-refused\\u0000<message>".
"""
import collections
import glob
import json
import sys

ROOT = sys.argv[1].rstrip('/')
REFUSED = '\u0000hashline-refused\u0000'


def bucket(message):
    for key, label in [('pos is required', 'no pos (old format)'), ('not a LINE#ID tag', 'pos not a tag'),
                       ('does not match line', 'stale/wrong tag'), ('the file has', 'line out of range'),
                       ('nothing would change', 'no change'), ('cannot read', 'file missing'),
                       ('op must be', 'bad op'), ('needs lines', 'insert without lines'), ('comes before', 'end before pos')]:
        if key in message:
            return label
    return 'other: ' + message[:60]


def main():
    print(f"{'arm':9} {'trials':>6} {'score':>6} {'edits/t':>7} {'edit ok':>8} {'fail':>6} {'t w/ fail':>9} {'writes/t':>8}")
    reasons = {}
    for arm in ['literal', 'hashline']:
        tot = collections.Counter()
        why = collections.Counter()
        n = scored = 0
        for d in glob.glob(f'{ROOT}/{arm}/*/*/'):
            if not glob.glob(d + 'agent'):
                continue
            n += 1
            try:
                tot['reward'] += float(open(d + 'verifier/reward.txt').read().strip())
                scored += 1
            except (OSError, ValueError):
                pass
            failed = False
            for f in glob.glob(d + 'agent/events-[0-9]*.jsonl'):
                calls = {}
                for line in open(f):
                    try:
                        e = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if e.get('type') == 'tool_call':
                        calls[e['callId']] = e
                        if e['tool'] == 'write':
                            tot['write'] += 1
                    elif e.get('type') == 'tool_result':
                        c = calls.get(e.get('callId'))
                        if not c or c['tool'] != 'edit':
                            continue
                        tot['edit'] += 1
                        if e.get('status') != 'error':
                            tot['ok'] += 1
                            continue
                        failed = True
                        old = str(c['input'].get('old_string', ''))
                        if old.startswith(REFUSED):
                            why[bucket(old[len(REFUSED):])] += 1
                        else:
                            r = e.get('result') or ''
                            why['DSH: not found' if 'was not found' in r else 'DSH: same text' if 'must differ' in r else 'DSH: ' + r[:50]] += 1
            tot['tfail'] += failed
        reasons[arm] = why
        e = max(tot['edit'], 1)
        print(f"{arm:9} {n:>6} {tot['reward'] / max(scored, 1) * 100:6.1f} {tot['edit'] / max(n, 1):7.2f} {tot['ok'] / e:8.1%} {(tot['edit'] - tot['ok']) / e:6.1%} {tot['tfail']:>9} {tot['write'] / max(n, 1):8.2f}")
    for arm, why in reasons.items():
        print(f'\n{arm} edit failures:')
        for k, v in why.most_common():
            print(f'  {v:5} {k}')


if __name__ == '__main__':
    main()
