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
docker run --rm --platform "$PLATFORM" ${NET[@]+"${NET[@]}"} -v "$OUT:/out" node:24-bookworm bash -c "
  set -euo pipefail
  npm install -g --no-fund --no-audit --prefix /opt/rae-node @deepseek-ai/dsh@${DSH_VERSION} pnpm
  cp /usr/local/bin/node /opt/rae-node/bin/node
  /opt/rae-node/bin/node /opt/rae-node/bin/dsh --version
  tar -czf /out/${NAME} -C /opt rae-node
"
ls -lh "$OUT/$NAME"
