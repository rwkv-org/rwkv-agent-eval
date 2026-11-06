#!/usr/bin/env bash
# Mirror what a remote Harbor host needs to run the eval, then check it.
#
#   scripts/sync-server.sh user@host [remote parent dir, default ~/Projects]
#
# Copies (rsync -z --partial, incremental, resumable): this repo with .git
# (run provenance reads the commit) and built tasks under build/; the sibling
# ../dsh-rwkv-plugin's runtime files with .git. Not copied: runs/, .cache/
# (toolchains and datasets are built/downloaded on the host, which has its own
# network), the plugin's bench/ and traces/.
# Then on the host: installs Harbor 0.25.0 with uv if missing, builds the
# toolchain for its arch if missing, checks Docker, prints the run command.
set -euo pipefail
HOST="${1:?usage: sync-server.sh user@host [remote parent dir]}"
PARENT="${2:-Projects}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$(cd "$HERE/../dsh-rwkv-plugin" && pwd)"

ssh "$HOST" "mkdir -p $PARENT"
RSYNC=(rsync -az --partial --timeout=60 --info=stats1,progress2)
# Toolchain label (harbor_agent.py default). `dsh-<commit>` labels are DSH built
# from source: send the packed tarballs; the host overlays them on its own
# npm build of BASE_DSH (backends/dsh/overlay-toolchain.sh).
DSH="$2"; BASE_DSH="$3"
A=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
if [ ! -f ".cache/rae-node-$DSH-linux-$A.tar.gz" ]; then
  if [[ "$DSH" == dsh-* ]]; then
    [ -f ".cache/rae-node-$BASE_DSH-linux-$A.tar.gz" ] || backends/dsh/build-toolchain.sh "$BASE_DSH" "linux/$A"
    backends/dsh/overlay-toolchain.sh ".cache/rae-node-$BASE_DSH-linux-$A.tar.gz" ".cache/dsh-packs/$DSH" "$DSH" | grep -v '^kept from npm'
  else
    backends/dsh/build-toolchain.sh "$DSH" "linux/$A"
  fi
fi
ls -lh .cache/rae-node-*.tar.gz
echo "eval $(git rev-parse --short HEAD)$(git status --porcelain | grep -q . && echo '*'), plugin $(git -C ../dsh-rwkv-plugin rev-parse --short HEAD)"
REMOTE
echo "Run there:  cd $PARENT/rwkv-agent-eval && scripts/calibrate.sh <rwkv_url> [concurrency]"
