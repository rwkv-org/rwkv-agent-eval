#!/usr/bin/env bash
# Scored eval run: a bank k times against one endpoint, optionally with an adapter.
#
#   [BACKEND=dsh|pi] [CONTAINER_URL=...] scripts/eval-run.sh <rwkv_url> <tasks dir> <name> [k=2] [concurrency=48] [adapter id|-] [harbor args...]
#
# BACKEND picks the agent harness (scripts/backend.sh): dsh (default) or pi.
#
# Extra args go to `harbor run`, e.g. --agent-timeout-multiplier 5 for an adapter
# (rwkv_lightning serves adapter requests ~4.5x slower; same compute budget as the base).
#
# Output: runs/eval-<name>-<UTC time>/ (a Harbor job dir; resume with `harbor jobs resume`).
# The adapter (rwkv_lightning MiSS/NoRA id) must already be registered on the server
# (GET /v1/adapters); the run fails fast otherwise. Provenance (model, adapter,
# DSH/plugin/eval commits) goes into every trial's agent/provenance.json.
set -euo pipefail
URL="${1:?usage: eval-run.sh <rwkv_url> <tasks dir> <name> [k] [concurrency] [adapter]}"
TASKS="${2:?tasks dir}"; NAME="${3:?name}"; K="${4:-2}"; N="${5:-48}"; ADAPTER="${6:-}"; [ "$ADAPTER" = - ] && ADAPTER=
EXTRA=("${@:7}")
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH" PYTHONPATH=.
source scripts/backend.sh   # AGENT, MOUNTS, PROBE, AK
KEY=(); [ -n "${RWKV_API_KEY:-}" ] && KEY=(-H "Authorization: Bearer $RWKV_API_KEY")
if [ -n "$ADAPTER" ]; then
  curl -sf "${KEY[@]}" "$URL/v1/adapters" | python3 -c 'import json,sys; ids={a["id"] for a in json.load(sys.stdin)["data"]}; sys.exit(0 if sys.argv[1] in ids else 1)' "$ADAPTER" \
    || { echo "adapter $ADAPTER is not registered on $URL"; exit 1; }
  AK+=(--ak adapter="$ADAPTER")
fi
echo "base image $(scripts/prepare-base-image.sh)"   # shared image for bank/prebuilt.py tasks (no per-task build)
harbor run -p "$PROBE" -a "$AGENT" "${AK[@]}" --mounts "$MOUNTS" -k 3 -n 3 -o "runs/probe/$NAME-$$" -q >/dev/null 2>&1 || true
P=$(ls -dt "runs/probe/$NAME-$$"/*/ | head -1)   # own dir: parallel launches must not read each other's probe
PASS=$(cat "$P"/*/verifier/reward.txt 2>/dev/null | grep -c '^1' || true)
echo "$BACKEND probe: $PASS/3 ($P)"
[ "$PASS" -ge 2 ] || { echo "$BACKEND probe failing: fix the image/endpoint first"; exit 1; }
OUT="runs/eval-$NAME-$(date -u +%Y%m%dT%H%M%S)"
echo "$(ls "$TASKS" | wc -l) tasks x $K at concurrency $N, adapter ${ADAPTER:--}, backend $BACKEND -> $OUT"
harbor run -p "$TASKS" -a "$AGENT" "${AK[@]}" --mounts "$MOUNTS" -k "$K" -n "$N" -o "$OUT" "${EXTRA[@]}"
