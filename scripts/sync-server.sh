#!/usr/bin/env bash
# Mirror what a remote Harbor host needs to run the eval, then check it.
#
#   scripts/sync-server.sh user@host [remote parent dir, default ~/Projects]
#
# Copies (rsync, incremental): this repo with .git (run provenance reads the
# commit), built tasks under build/, the amd64 toolchain and downloaded
# datasets under .cache/; the sibling ../dsh-rwkv-plugin with .git. Not
# copied: runs/, other-arch toolchains, the DSH source build tree.
# Then on the host: installs Harbor 0.25.0 with uv if missing, checks Docker,
# and prints the run command.
set -euo pipefail
HOST="${1:?usage: sync-server.sh user@host [remote parent dir]}"
PARENT="${2:-Projects}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$(cd "$HERE/../dsh-rwkv-plugin" && pwd)"
ARCH="${ARCH:-amd64}"

ssh "$HOST" "mkdir -p $PARENT"
rsync -az --delete --info=stats1 \
  --exclude runs/ --exclude 'build/codex/' --exclude '.cache/dsh-src-*' \
  --exclude ".cache/rae-node-*-linux-arm64.tar.gz" --exclude __pycache__ \
  "$HERE/" "$HOST:$PARENT/rwkv-agent-eval/"
rsync -az --delete --info=stats1 --exclude node_modules --exclude .claude \
  "$PLUGIN/" "$HOST:$PARENT/dsh-rwkv-plugin/"

ssh "$HOST" bash -s -- "$PARENT" <<'REMOTE'
set -euo pipefail
cd "$1/rwkv-agent-eval"
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
harbor --version 2>/dev/null | grep -q '^0.25.0' || uv tool install --force harbor==0.25.0
echo "harbor $(harbor --version)"
docker info --format 'docker {{.ServerVersion}}, {{.NCPU}} CPUs, {{.MemTotal}} bytes' 
uname -m; nproc; free -g | head -2
ls -lh .cache/rae-node-*.tar.gz
echo "eval $(git rev-parse --short HEAD)$(git status --porcelain | grep -q . && echo '*'), plugin $(git -C ../dsh-rwkv-plugin rev-parse --short HEAD)"
REMOTE
echo "Run there:  cd $PARENT/rwkv-agent-eval && scripts/calibrate.sh <rwkv_url> [concurrency]"
