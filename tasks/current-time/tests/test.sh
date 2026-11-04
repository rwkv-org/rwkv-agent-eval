#!/usr/bin/env bash
TESTS="${RAE_TESTS_DIR:-/tests}"
LOGS="${RAE_LOGS_DIR:-/logs}"
mkdir -p "$LOGS/verifier"
if python3 "$TESTS/check.py" "$LOGS/agent/final.txt"; then echo 1 > "$LOGS/verifier/reward.txt"; else echo 0 > "$LOGS/verifier/reward.txt"; fi
