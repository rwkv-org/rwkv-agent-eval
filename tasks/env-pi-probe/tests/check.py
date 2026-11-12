"""Environment probe (Pi backend): pass only if Pi's bash tool was called,
completed (not errored) with output naming the file, and the reply names it.
Pi's training allowlist is read/write/edit/bash (no grep tool), so this checks
the shell path: a broken /bin/bash, missing coreutils or an unseeded workspace
fails here instead of silently lowering every score."""
import json
import sys

calls, results = {}, {}
for line in open('/logs/agent/events.jsonl', errors='replace'):
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        continue
    if e.get('type') == 'tool_call':
        calls[e.get('callId')] = e.get('tool')
    elif e.get('type') == 'tool_result':
        results[e.get('callId')] = e
shells = [results.get(cid) for cid, tool in calls.items() if tool == 'bash']
final = open('/logs/agent/final.txt', errors='replace').read()
print('bash calls:', [(r or {}).get('status') for r in shells])
for r in shells:
    if r and r.get('status') != 'completed':
        print('BASH TOOL ERROR:', str(r.get('result'))[:500])
ok = any(r and r.get('status') == 'completed' and 'ledger.py' in str(r.get('result')) for r in shells)
ok = ok and 'ledger.py' in final
print('PASS' if ok else 'FAIL', repr(final[:200]))
sys.exit(0 if ok else 1)
