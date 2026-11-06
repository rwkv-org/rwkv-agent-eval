"""Environment probe: pass only if DSH's grep tool was called and completed
(not errored), and the reply names the file. Fails loudly when the image's
grep backend (ripgrep) is broken, which pushes the model into complex bash."""
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
greps = [results.get(cid) for cid, tool in calls.items() if tool == 'grep']
final = open('/logs/agent/final.txt', errors='replace').read()
print('grep calls:', [(r or {}).get('status') for r in greps])
for r in greps:
    if r and r.get('status') != 'completed':
        print('GREP TOOL ERROR:', str(r.get('result'))[:500])
ok = any(r and r.get('status') == 'completed' and 'ledger.py' in str(r.get('result')) for r in greps)
ok = ok and 'ledger.py' in final
print('PASS' if ok else 'FAIL', repr(final[:200]))
sys.exit(0 if ok else 1)
