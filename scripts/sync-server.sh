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
"${RSYNC[@]}" --delete --exclude /runs/ --exclude /.cache/ --exclude /build/codex/ --exclude __pycache__ \
  "$HERE/" "$HOST:$PARENT/rwkv-agent-eval/"
"${RSYNC[@]}" --delete --exclude /node_modules/ --exclude /.claude/ --exclude /bench/ --exclude /traces/ \
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
DSH=$(sed -n "s/.*dsh_version: str = '\([^']*\)'.*/\1/p" backends/dsh/harbor_agent.py)
A=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
[ -f ".cache/rae-node-$DSH-linux-$A.tar.gz" ] || backends/dsh/build-toolchain.sh "$DSH" "linux/$A"
ls -lh .cache/rae-node-*.tar.gz
echo "eval $(git rev-parse --short HEAD)$(git status --porcelain | grep -q . && echo '*'), plugin $(git -C ../dsh-rwkv-plugin rev-parse --short HEAD)"
REMOTE
echo "Run there:  cd $PARENT/rwkv-agent-eval && scripts/calibrate.sh <rwkv_url> [concurrency]"
