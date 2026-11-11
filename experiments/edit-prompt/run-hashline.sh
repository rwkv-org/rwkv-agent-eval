#!/usr/bin/env bash
# Base model (no adapter), literal edit vs hashline edit (plugin branch hashline-edit synced to
# ../dsh-rwkv-plugin-hashline), same 416-task edit subset, DSH 0.2.2-rc.1, no date line.
# Usage (eval root on the server): experiments/edit-prompt/run-hashline.sh [k] [per-arm concurrency]
set -euo pipefail
cd "$(dirname "$0")/../.."
export PATH="$HOME/.local/bin:$PATH" PYTHONPATH=.
K=${1:-1}; N=${2:-16}
PLUGIN=$(cd ../dsh-rwkv-plugin-hashline && pwd)
M=$(scripts/prepare-toolchain.sh 0.2.2-rc.1)
INC=(); while read -r t; do [ -n "$t" ] && INC+=(-i "$t"); done < experiments/edit-prompt/tasks.txt
STAMP=$(date -u +%Y%m%dT%H%M%S)
for V in literal hashline; do
  CFG=(); [ "$V" = hashline ] && CFG=(--ak plugin_config=experiments/edit-prompt/hashline.json)
  OUT=runs/edit-hashline-base-$STAMP/$V
  mkdir -p "$OUT"
  harbor run -p build/bank-full-1019 "${INC[@]}" -a backends.dsh.harbor_agent:DshRwkv \
    --ak rwkv_url=http://100.64.0.8:8060 --ak plugin_dir="$PLUGIN" --ak dsh_version=0.2.2-rc.1 "${CFG[@]}" \
    --mounts "$M" -k "$K" -n "$N" -o "$OUT" --agent-timeout-multiplier 5 > "$OUT.log" 2>&1 &
  echo "$V -> $OUT (pid $!)"
done
wait
echo done
