#!/usr/bin/env python3
"""Failure-pattern counts for one Harbor job dir.

    python3 runner/diagnose.py runs/<run>  [--list]

Reads each task's event stream (events.jsonl; DSH writes it natively, the Pi
backend converts Pi's session log to the same schema) and tags it:
  fallback     the final message is the plugin's "could not turn it into an
               answer" template (the agent gave up after tool calls)
  not_found    some read/edit failed with "not found" (often a bad path)
  edit_miss    an edit's old_string did not match the file
  no_tools     no tool call at all
  tool_in_text the final message contains a raw <tool_call> (never executed)
  timeout / exception  the trial did not finish normally
  from the final event's reason.kind (the Pi backend writes these):
  engine_error the provider ended the turn with an error (rwkv-pi refused an
               unterminated/unsafe continuation, engine unreachable, ...)
  max_tokens   the last reply hit RWKV_MAX_TOKENS
  aborted      the turn budget (max_steps) stopped the run
  Pi backend, from rwkv-pi's error text and the request trace:
  unknown_tool    called a tool outside the allowlist (e.g. execute_bash, run_shell)
  loop_guard      rwkv-pi's RWKV_TOOL_LOOP guard ended the turn (same failing call 3x)
  truncated_call  rwkv-pi refused a tool call cut off before its closing tag
  unclosed_think  the reply ended inside a reasoning block
  context_overflow the prompt outgrew the context window (rwkv-pi never truncates;
                  Pi reports this as "Connection error.")
"""
import argparse
import collections
import json
from pathlib import Path

FALLBACK = 'could not turn it into an answer'
# rwkv-pi error texts on the final event -> tag (first match wins)
PI_ERRORS = [('RWKV_TOOL_LOOP', 'loop_guard'), ('Truncated tool call', 'truncated_call'),
             ('Unclosed reasoning block', 'unclosed_think')]


def context_overflow(agent_dir: Path) -> bool:
    """Pi backend: the last /tokens/count in the trace exceeds the context window
    the run used (provenance.json)."""
    try:
        window = json.loads((agent_dir / 'provenance.json').read_text()).get('context_window')
    except (OSError, ValueError):
        return False
    counts = sorted((agent_dir / 'trace').glob('*.request.json')) if window else []
    for req in reversed(counts):
        try:
            if not json.loads(req.read_text()).get('path', '').endswith('/tokens/count'):
                continue
            return int(json.loads(req.with_name(req.name.replace('request.json', 'response.txt')).read_text())['tokens']) > window
        except (OSError, ValueError, KeyError, TypeError):
            return False
    return False


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
    last = next((e for e in reversed(events) if e.get('type') == 'final'), {})
    final = last.get('text', '') or ''
    kind = (last.get('reason') or {}).get('kind') if isinstance(last.get('reason'), dict) else None
    error = str((last.get('reason') or {}).get('error', '')) if isinstance(last.get('reason'), dict) else ''
    pi_tag = next((tag for needle, tag in PI_ERRORS if needle in error), None)
    if pi_tag:
        out.add(pi_tag)
    elif kind in ('error', 'max_tokens', 'aborted'):
        out.add({'error': 'engine_error'}.get(kind, kind))
    if context_overflow(events_path.parent):
        out.discard('engine_error')
        out.add('context_overflow')
    if not calls:
        out.add('no_tools')
    if FALLBACK in final:
        out.add('fallback')
    if '<tool_call>' in final:
        out.add('tool_in_text')
    for r in results:
        text = json.dumps(r.get('result', ''))
        if r.get('status') == 'error' and text.startswith('"Tool ') and text.endswith(' not found"'):
            out.add('unknown_tool')
        elif r.get('status') == 'error' and 'not found' in text:
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
