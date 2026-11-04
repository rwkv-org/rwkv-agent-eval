#!/usr/bin/env bash
# Answer task: grades the agent's final message (see README, "Backend contract").
mkdir -p /logs/verifier
if python3 /tests/check.py /logs/agent/final.txt; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
