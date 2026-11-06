#!/usr/bin/env bash
# Unpack the agent toolchain once on the Harbor host so trials can mount it
# read-only instead of uploading and unpacking 237 MB each (the bottleneck at
# high concurrency). Prints the --mounts value for `harbor run`.
#
#   scripts/prepare-toolchain.sh [dsh label, default: harbor_agent.py's] [arch]
#
# Output dir: .cache/toolchain/<label>-linux-<arch>/rae-node, with the web
# replay plugin inside the DSH package and a RAE_TOOLCHAIN marker (label,
# tarball and plugin sha256) that the agent checks before trusting the mount.
# Re-unpacks whenever the tarball or plugin changed.
set -euo pipefail
cd "$(dirname "$0")/.."
LABEL="${1:-$(sed -n "s/.*dsh_version: str = '\([^']*\)'.*/\1/p" backends/dsh/harbor_agent.py)}"
ARCH="${2:-$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')}"
TGZ=".cache/rae-node-$LABEL-linux-$ARCH.tar.gz"
DIR="$PWD/.cache/toolchain/$LABEL-linux-$ARCH"
REPLAY=backends/dsh/web-replay.mjs
[ -f "$TGZ" ] || { echo "missing $TGZ" >&2; exit 1; }
sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1 || shasum -a 256 "$1" | cut -d' ' -f1; }
MARK=$(printf '{"label": "%s", "tarball_sha256": "%s", "replay_sha256": "%s"}' "$LABEL" "$(sha "$TGZ")" "$(sha "$REPLAY")")
if [ "$(cat "$DIR/rae-node/RAE_TOOLCHAIN" 2>/dev/null)" != "$MARK" ]; then
  rm -rf "$DIR" && mkdir -p "$DIR"
  tar -xzf "$TGZ" -C "$DIR"
  cp "$REPLAY" "$DIR/rae-node/lib/node_modules/@deepseek-ai/dsh/rae-web-replay.mjs"
  printf '%s' "$MARK" > "$DIR/rae-node/RAE_TOOLCHAIN"
  chmod -R a+rX "$DIR"
fi
printf '[{"type": "bind", "source": "%s/rae-node", "target": "/opt/rae-node", "read_only": true}]\n' "$DIR"
