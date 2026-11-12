#!/usr/bin/env bash
# Unpack the agent toolchain once on the Harbor host so trials can mount it
# read-only instead of uploading and unpacking it each time (the bottleneck at
# high concurrency). Prints the --mounts value for `harbor run`.
#
#   scripts/prepare-toolchain.sh [dsh label, default: harbor_agent.py's] [arch]
#   scripts/prepare-toolchain.sh pi [pi label, default: ../rwkv-pi HEAD] [arch]
#
# DSH: .cache/toolchain/<label>-linux-<arch>/rae-node -> /opt/rae-node, with the
#      web replay plugin inside the DSH package.
# Pi:  .cache/toolchain/pi-<label>-linux-<arch>/rae-pi -> /opt/rae-pi (Node, Pi
#      source, compiled rwkv-pi; built by backends/pi/build-toolchain.sh).
# Both get a RAE_TOOLCHAIN marker (label and sha256 of what was unpacked) that
# the agent checks before trusting the mount. Re-unpacks whenever it changed.
set -euo pipefail
cd "$(dirname "$0")/.."
sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1 || shasum -a 256 "$1" | cut -d' ' -f1; }
host_arch() { uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/'; }
if [ "${1:-}" = pi ]; then
  LABEL="${2:-$(scripts/pi-label.sh)}"
  ARCH="${3:-$(host_arch)}"
  TGZ=".cache/rae-pi-$LABEL-linux-$ARCH.tar.gz"
  DIR="$PWD/.cache/toolchain/pi-$LABEL-linux-$ARCH"
  [ -f "$TGZ" ] || { echo "missing $TGZ: run backends/pi/build-toolchain.sh" >&2; exit 1; }
  MARK=$(printf '{"label": "%s", "tarball_sha256": "%s"}' "$LABEL" "$(sha "$TGZ")")
  if [ "$(cat "$DIR/rae-pi/RAE_TOOLCHAIN" 2>/dev/null)" != "$MARK" ]; then
    rm -rf "$DIR" && mkdir -p "$DIR"
    tar -xzf "$TGZ" -C "$DIR"
    printf '%s' "$MARK" > "$DIR/rae-pi/RAE_TOOLCHAIN"
    chmod -R a+rX "$DIR"
  fi
  printf '[{"type": "bind", "source": "%s/rae-pi", "target": "/opt/rae-pi", "read_only": true}]\n' "$DIR"
  exit 0
fi
LABEL="${1:-$(sed -n "s/.*dsh_version: str = '\([^']*\)'.*/\1/p" backends/dsh/harbor_agent.py)}"
ARCH="${2:-$(host_arch)}"
TGZ=".cache/rae-node-$LABEL-linux-$ARCH.tar.gz"
DIR="$PWD/.cache/toolchain/$LABEL-linux-$ARCH"
REPLAY=backends/dsh/web-replay.mjs
[ -f "$TGZ" ] || { echo "missing $TGZ" >&2; exit 1; }
MARK=$(printf '{"label": "%s", "tarball_sha256": "%s", "replay_sha256": "%s"}' "$LABEL" "$(sha "$TGZ")" "$(sha "$REPLAY")")
if [ "$(cat "$DIR/rae-node/RAE_TOOLCHAIN" 2>/dev/null)" != "$MARK" ]; then
  rm -rf "$DIR" && mkdir -p "$DIR"
  tar -xzf "$TGZ" -C "$DIR"
  cp "$REPLAY" "$DIR/rae-node/lib/node_modules/@deepseek-ai/dsh/rae-web-replay.mjs"
  printf '%s' "$MARK" > "$DIR/rae-node/RAE_TOOLCHAIN"
  chmod -R a+rX "$DIR"
fi
printf '[{"type": "bind", "source": "%s/rae-node", "target": "/opt/rae-node", "read_only": true}]\n' "$DIR"
