#!/usr/bin/env bash
# Build the self-contained Node + DSH + pnpm tree the Harbor backend uploads
# into task containers (no network install per trial). Output:
#   .cache/rae-node-<dsh version>-linux-<arch>.tar.gz   (unpacks to /opt/rae-node)
# Needs a glibc container at run time (Debian/Ubuntu task images; not Alpine).
#
#   backends/dsh/build-toolchain.sh [dsh version] [linux/arm64|linux/amd64]
#
# Network: RAE_PROXY=http://host:port routes npm through a proxy (from inside
# the container, the host is host.docker.internal); NPM_REGISTRY picks a mirror
# (e.g. https://registry.npmmirror.com).
# Hosts that cannot pull node:24-bookworm: RAE_BUILD_IMAGE=<any glibc Debian/Ubuntu
# image already present> plus RAE_NODE=<official linux Node >= 24.9 binary>, which
# is mounted in and used instead of the image's node.
set -euo pipefail
DSH_VERSION="${1:-0.2.1-rc.5}"
PLATFORM="${2:-linux/$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/.cache"
NAME="rae-node-${DSH_VERSION}-${PLATFORM//\//-}.tar.gz"
mkdir -p "$OUT"
NET=()
if [ -n "${RAE_PROXY:-}" ]; then
  NET+=(-e "HTTP_PROXY=$RAE_PROXY" -e "HTTPS_PROXY=$RAE_PROXY" -e "npm_config_proxy=$RAE_PROXY" -e "npm_config_https_proxy=$RAE_PROXY")
fi
if [ -n "${NPM_REGISTRY:-}" ]; then NET+=(-e "npm_config_registry=$NPM_REGISTRY"); fi
IMAGE="${RAE_BUILD_IMAGE:-node:24-bookworm}"
MOUNT=(); PRE=""
if [ -n "${RAE_NODE:-}" ]; then
  NODE_DIR="$(cd "$(dirname "$(readlink -f "$RAE_NODE")")/.." && pwd)"
  MOUNT=(-v "$NODE_DIR:/opt/host-node:ro")
  PRE="mkdir -p /usr/local/bin && ln -sf /opt/host-node/bin/node /usr/local/bin/node && export PATH=/opt/host-node/bin:\$PATH;"
fi
docker run --rm --platform "$PLATFORM" ${NET[@]+"${NET[@]}"} ${MOUNT[@]+"${MOUNT[@]}"} -v "$OUT:/out" "$IMAGE" bash -c "
  set -euo pipefail
  $PRE
  # npm >= 11.19 skips dependency install scripts unless allowed (native addons, DSH's subprocess helper).
  export npm_config_allow_scripts=pnpm,@deepseek-ai/dsh-subprocess-local,koffi,node-pty,@google/genai,protobufjs
  npm install -g --no-fund --no-audit --prefix /opt/rae-node @deepseek-ai/dsh@${DSH_VERSION} pnpm
  cp \$(readlink -f \$(command -v node)) /opt/rae-node/bin/node
  /opt/rae-node/bin/node /opt/rae-node/bin/dsh --version
  tar -czf /out/${NAME} -C /opt rae-node
"
ls -lh "$OUT/$NAME"
