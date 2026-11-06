#!/usr/bin/env bash
# Mirror what a remote Harbor host needs to run the eval, then prepare it.
#
#   scripts/sync-server.sh user@host [remote parent dir, default ~/Projects]
#
# Copies (rsync -z --partial, incremental, resumable): this repo with .git
# (run provenance reads the commit) and built tasks under build/; the sibling
# ../dsh-rwkv-plugin's runtime files with .git. Not copied: runs/, .cache/
# (toolchains and datasets are built/downloaded on the host, which has its own
# network), the plugin's bench/ and traces/.
#
# Toolchain: the label is harbor_agent.py's default dsh_version. A `dsh-<commit>`
# label is DSH built from source: its packed tarballs (.cache/dsh-packs/<label>,
# 29 MB) are sent and overlaid on the host's own npm build of BASE_DSH
# (backends/dsh/overlay-toolchain.sh). Any other label is an npm version,
# built on the host with build-toolchain.sh.
#
# Then on the host: installs Harbor 0.25.0 (uv) and the docker compose plugin
# (user-level) if missing, checks Docker.
set -euo pipefail
HOST="${1:?usage: sync-server.sh user@host [remote parent dir]}"
PARENT="${2:-Projects}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$(cd "$HERE/../dsh-rwkv-plugin" && pwd)"
DSH=$(sed -n "s/.*dsh_version: str = '\([^']*\)'.*/\1/p" "$HERE/backends/dsh/harbor_agent.py")
BASE_DSH=0.2.2-alpha.3
RSYNC=(rsync -az --partial --timeout=60 --info=stats1,progress2)

ssh "$HOST" "mkdir -p $PARENT/rwkv-agent-eval/.cache/dsh-packs"
"${RSYNC[@]}" --delete --exclude /runs/ --exclude /.cache/ --exclude /build/codex/ --exclude __pycache__ \
  "$HERE/" "$HOST:$PARENT/rwkv-agent-eval/"
"${RSYNC[@]}" --delete --exclude /node_modules/ --exclude /.claude/ --exclude /bench/ --exclude /traces/ \
  "$PLUGIN/" "$HOST:$PARENT/dsh-rwkv-plugin/"
if [[ "$DSH" == dsh-* ]]; then
  "${RSYNC[@]}" "$HERE/.cache/dsh-packs/$DSH/" "$HOST:$PARENT/rwkv-agent-eval/.cache/dsh-packs/$DSH/"
fi

ssh "$HOST" bash -s -- "$PARENT" "$DSH" "$BASE_DSH" <<'REMOTE'
set -euo pipefail
cd "$1/rwkv-agent-eval"
DSH="$2"; BASE_DSH="$3"
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
harbor --version 2>/dev/null | grep -q '^0.25.0' || uv tool install --force harbor==0.25.0
echo "harbor $(harbor --version)"
A=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
if [ ! -f ".cache/rae-node-$DSH-linux-$A.tar.gz" ]; then
  if [[ "$DSH" == dsh-* ]]; then
    [ -f ".cache/rae-node-$BASE_DSH-linux-$A.tar.gz" ] || backends/dsh/build-toolchain.sh "$BASE_DSH" "linux/$A"
    backends/dsh/overlay-toolchain.sh ".cache/rae-node-$BASE_DSH-linux-$A.tar.gz" ".cache/dsh-packs/$DSH" "$DSH" | grep -v '^kept from npm'
  else
    backends/dsh/build-toolchain.sh "$DSH" "linux/$A"
  fi
fi
docker info --format 'docker {{.ServerVersion}}, {{.NCPU}} CPUs, {{.MemTotal}} bytes'
# Harbor drives containers through `docker compose`; install the user-level plugin if missing.
if ! docker compose version >/dev/null 2>&1; then
  mkdir -p ~/.docker/cli-plugins
  V=$(curl -fsSL https://api.github.com/repos/docker/compose/releases/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
  curl -fsSL -o ~/.docker/cli-plugins/docker-compose "https://github.com/docker/compose/releases/download/$V/docker-compose-linux-$(uname -m)"
  chmod +x ~/.docker/cli-plugins/docker-compose
fi
docker compose version
ls -lh .cache/rae-node-*.tar.gz
echo "eval $(git rev-parse --short HEAD)$(git status --porcelain | grep -q . && echo '*'), plugin $(git -C ../dsh-rwkv-plugin rev-parse --short HEAD)"
REMOTE
echo "Run there:  cd $PARENT/rwkv-agent-eval && scripts/calibrate.sh <rwkv_url> [concurrency]"
