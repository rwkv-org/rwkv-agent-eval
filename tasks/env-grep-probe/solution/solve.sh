#!/usr/bin/env bash
# Oracle: what a passing agent leaves behind.
printf '%s\n' '{"type":"tool_call","callId":"c1","tool":"grep"}' '{"type":"tool_result","callId":"c1","status":"completed","result":"src/billing/ledger.py:2"}' > /logs/agent/events.jsonl
echo 'ORBIT_LEDGER_KEY 出现在 src/billing/ledger.py。' > /logs/agent/final.txt
