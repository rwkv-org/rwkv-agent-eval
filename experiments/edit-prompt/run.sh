#!/usr/bin/env bash
# Edit-tool prompt experiment: the 416 tasks that used edit in >=2 of the 2026-11-11 full runs,
# new adapter in its training env (DSH 0.2.2-rc.1 + date line), 4 variants run side by side.
# Usage (on the eval server, from the eval root): experiments/edit-prompt/run.sh [k] [per-variant concurrency]
set -euo pipefail
cd "$(dirname "$0")/../.."
export PATH="$HOME/.local/bin:$PATH" PYTHONPATH=.
K=${1:-2}; N=${2:-24}
echo "base image $(scripts/prepare-base-image.sh)"
M=$(scripts/prepare-toolchain.sh 0.2.2-rc.1)
INC=(); while read -r t; do [ -n "$t" ] && INC+=(-i "$t"); done < experiments/edit-prompt/tasks.txt
STAMP=$(date -u +%Y%m%dT%H%M%S)
for V in base desc rule both; do
  CFG=(); [ "$V" != base ] && CFG=(--ak plugin_config=experiments/edit-prompt/$V.json)
  OUT=runs/edit-prompt-$STAMP/$V
  mkdir -p "$OUT"
  harbor run -p build/bank-full-1019 "${INC[@]}" -a backends.dsh.harbor_agent:DshRwkv \
    --ak rwkv_url=http://100.64.0.8:8060 --ak adapter=g1l-nora-r16-261111 \
    --ak dsh_version=0.2.2-rc.1 --ak time_zone=Asia/Shanghai "${CFG[@]}" \
    --mounts "$M" -k "$K" -n "$N" -o "$OUT" --agent-timeout-multiplier 5 > "$OUT.log" 2>&1 &
  echo "$V -> $OUT (pid $!)"
done
wait
echo done
