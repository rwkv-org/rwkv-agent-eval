#!/usr/bin/env bash
# Calibration run: every candidate task k times against one endpoint.
#
#   scripts/calibrate.sh <rwkv_url> [concurrency=64] [tasks dir=build/candidates] [k=3]
#
# Output: runs/calib-<UTC time>/ (a Harbor job dir; resume with `harbor jobs resume`).
# Probe first: the grep probe must pass, or the image is broken and the whole
# run would measure the environment instead of the model.
set -euo pipefail
URL="${1:?usage: calibrate.sh <rwkv_url> [concurrency] [tasks dir] [k]}"
N="${2:-64}"; TASKS="${3:-build/candidates}"; K="${4:-3}"
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH" PYTHONPATH=.
AGENT=backends.dsh.harbor_agent:DshRwkv
harbor run -p tasks/env-grep-probe -a "$AGENT" --ak rwkv_url="$URL" -k 3 -n 3 -o runs/probe -q >/dev/null 2>&1 || true
P=$(ls -dt runs/probe/*/ | head -1)
PASS=$(cat "$P"/*/verifier/reward.txt 2>/dev/null | grep -c '^1' || true)
echo "grep probe: $PASS/3 ($P)"
[ "$PASS" -ge 2 ] || { echo "grep probe failing: fix the image before calibrating"; exit 1; }
OUT="runs/calib-$(date -u +%Y%m%dT%H%M%S)"
echo "calibrating $(ls "$TASKS" | wc -l) tasks x $K at concurrency $N -> $OUT"
harbor run -p "$TASKS" -a "$AGENT" --ak rwkv_url="$URL" -k "$K" -n "$N" -o "$OUT"
