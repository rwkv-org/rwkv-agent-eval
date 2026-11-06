#!/usr/bin/env bash
# Wait for the endpoint, resume an interrupted calibration job, then calibrate
# the open-source tasks (build/oss, from bank/prepare_oss.py).
#
#   scripts/calib-chain.sh <rwkv_url> <job dir to resume> [oss concurrency=60]
set -euo pipefail
URL="${1:?usage: calib-chain.sh <rwkv_url> <job dir> [oss concurrency]}"; JOB="$2"; N="${3:-60}"
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH" PYTHONPATH=.
until curl -sf -m 10 "${URL%/}/v1/models" >/dev/null; do echo "$(date '+%F %T') waiting for $URL"; sleep 30; done
echo "$(date '+%F %T') endpoint up; resuming $JOB"
harbor jobs resume "$JOB" -f CancelledError || echo "resume exited $?"
echo "$(date '+%F %T') main calibration done; open-source tasks next"
python3 bank/prepare_oss.py
scripts/calibrate.sh "$URL" "$N" build/oss 3
echo "$(date '+%F %T') chain done"
