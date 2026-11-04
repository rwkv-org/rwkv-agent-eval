#!/usr/bin/env bash
# Harbor runs this in the task workdir with /tests and /logs; the workspace
# runner sets RAE_TESTS_DIR / RAE_LOGS_DIR to host paths instead.
TESTS="${RAE_TESTS_DIR:-/tests}"
LOGS="${RAE_LOGS_DIR:-/logs}"
mkdir -p "$LOGS/verifier"
if python3 "$TESTS/check.py"; then echo 1 > "$LOGS/verifier/reward.txt"; else echo 0 > "$LOGS/verifier/reward.txt"; fi
