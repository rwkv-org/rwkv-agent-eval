#!/usr/bin/env bash
# Calibration run: every candidate task k times against one endpoint.
#
#   [BACKEND=dsh|pi] [CONTAINER_URL=...] scripts/calibrate.sh <rwkv_url> [concurrency=64] [tasks dir=build/candidates] [k=3]
#
# Output: runs/calib-<UTC time>/ (a Harbor job dir; resume with `harbor jobs resume`).
# Probe first: the grep probe must pass, or the image is broken and the whole
# run would measure the environment instead of the model.
set -euo pipefail
URL="${1:?usage: calibrate.sh <rwkv_url> [concurrency] [tasks dir] [k]}"
N="${2:-64}"; TASKS="${3:-build/candidates}"; K="${4:-3}"
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH" PYTHONPATH=.
echo "base image $(scripts/prepare-base-image.sh)"   # shared image for bank/prebuilt.py tasks (no per-task build)
source scripts/backend.sh   # AGENT, PROBE, AK; toolchain unpacked once, mounted read-only into every trial
harbor run -p "$PROBE" -a "$AGENT" "${AK[@]}" --mounts "$MOUNTS" -k 3 -n 3 -o runs/probe -q >/dev/null 2>&1 || true
P=$(ls -dt runs/probe/*/ | head -1)
PASS=$(cat "$P"/*/verifier/reward.txt 2>/dev/null | grep -c '^1' || true)
echo "$BACKEND probe: $PASS/3 ($P)"
[ "$PASS" -ge 2 ] || { echo "$BACKEND probe failing: fix the image/endpoint before calibrating"; exit 1; }
OUT="runs/calib-$BACKEND-$(date -u +%Y%m%dT%H%M%S)"
echo "calibrating $(ls "$TASKS" | wc -l) tasks x $K at concurrency $N -> $OUT"
harbor run -p "$TASKS" -a "$AGENT" "${AK[@]}" --mounts "$MOUNTS" -k "$K" -n "$N" -o "$OUT"
