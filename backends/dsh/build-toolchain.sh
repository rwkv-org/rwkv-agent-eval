#!/usr/bin/env bash
# Build the self-contained Node + DSH + pnpm tree the Harbor backend uploads
# into task containers (no network install per trial). Output:
#   .cache/rae-node-<dsh version>-linux-<arch>.tar.gz   (unpacks to /opt/rae-node)
# Needs a glibc container at run time (Debian/Ubuntu task images; not Alpine).
#
#   backends/dsh/build-toolchain.sh [dsh version] [linux/arm64|linux/amd64]
set -euo pipefail
DSH_VERSION="${1:-0.2.1-rc.5}"
PLATFORM="${2:-linux/$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/.cache"
NAME="rae-node-${DSH_VERSION}-${PLATFORM//\//-}.tar.gz"
mkdir -p "$OUT"
docker run --rm --platform "$PLATFORM" -v "$OUT:/out" node:24-bookworm bash -c "
  set -euo pipefail
  npm install -g --no-fund --no-audit --prefix /opt/rae-node @deepseek-ai/dsh@${DSH_VERSION} pnpm
  cp /usr/local/bin/node /opt/rae-node/bin/node
  /opt/rae-node/bin/node /opt/rae-node/bin/dsh --version
  tar -czf /out/${NAME} -C /opt rae-node
"
ls -lh "$OUT/$NAME"
