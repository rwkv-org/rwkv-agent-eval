#!/usr/bin/env bash
# Toolchain label of the rwkv-pi checkout as it is now (same rule as
# backends/pi/build-toolchain.sh and PiRwkv's default pi_label):
# rwkv-pi-<short HEAD>[-dirty if src/, package*.json or tsconfig.json changed].
#
#   scripts/pi-label.sh [rwkv-pi dir, default ../rwkv-pi]
set -euo pipefail
P="${1:-$(cd "$(dirname "$0")/../.." && pwd)/rwkv-pi}"
dirty=""; git -C "$P" diff --quiet HEAD -- src package.json package-lock.json tsconfig.json || dirty="-dirty"
echo "rwkv-pi-$(git -C "$P" rev-parse --short HEAD)$dirty"
