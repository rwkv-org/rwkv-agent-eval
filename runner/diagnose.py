#!/usr/bin/env python3
"""Failure-pattern counts for one Harbor job dir.

    python3 runner/diagnose.py runs/<run>  [--list]

Reads each task's DSH event stream (events.jsonl) and tags it:
  fallback     the final message is the plugin's "could not turn it into an
               answer" template (the agent gave up after tool calls)
  not_found    some read/edit failed with "not found" (often a bad path)
  edit_miss    an edit's old_string did not match the file
  no_tools     no tool call at all
  tool_in_text the final message contains a raw <tool_call> (never executed)
  timeout / exception  the trial did not finish normally
"""
import argparse
import collections
import json
from pathlib import Path

FALLBACK = 'could not turn it into an answer'


def trials(run: Path):
    for res in sorted(run.glob('*/result.json')):
        t = json.loads(res.read_text())
        reward = ((t.get('verifier_result') or {}).get('rewards') or {}).get('reward', 0.0)
        exc = (t.get('exception_info') or {}).get('exception_type')
        yield t['task_name'].split('/')[-1], reward, exc or 'ok', res.parent / 'agent' / 'events.jsonl'


def tags(events_path: Path, status: str):
    out = set()
    if status != 'ok':
        out.add('timeout' if 'imeout' in status else 'exception')
    if not events_path.exists():
        return out | {'no_events'}, 0
    events = []
    for line in events_path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    calls = [e for e in events if e.get('type') == 'tool_call']
    results = [e for e in events if e.get('type') == 'tool_result']
    final = next((e.get('text', '') for e in reversed(events) if e.get('type') == 'final'), '')
    if not calls:
        out.add('no_tools')
    if FALLBACK in final:
        out.add('fallback')
    if '<tool_call>' in final:
        out.add('tool_in_text')
    for r in results:
        text = json.dumps(r.get('result', ''))
        if r.get('status') == 'error' and 'not found' in text:
            out.add('edit_miss' if 'old_string' in text else 'not_found')
    return out, len(calls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    run = Path(a.run)
    counts, fail_counts = collections.Counter(), collections.Counter()
    n = passed = 0
    rows = []
    for tid, reward, status, ev in trials(run):
        t, ncalls = tags(ev, status)
        n += 1
        passed += reward >= 1
        counts.update(t)
        if reward < 1:
            fail_counts.update(t)
        rows.append((tid, reward, ncalls, sorted(t)))
    print(f'{run.name}: {passed}/{n} passed')
    print('tag            all  failed')
    for tag in sorted(counts, key=lambda k: -counts[k]):
        print(f'{tag:<14} {counts[tag]:>3}  {fail_counts[tag]:>6}')
    if a.list:
        for tid, reward, ncalls, t in sorted(rows):
            print(f'{reward:g}  {tid:<24} tools={ncalls:<3} {" ".join(t)}')


if __name__ == '__main__':
    main()
