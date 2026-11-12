#!/usr/bin/env bash
# Build the self-contained Pi + rwkv-pi tree the Pi backend uploads into task
# containers (no network install per trial). Output:
#   .cache/rae-pi-<label>-linux-<arch>.tar.gz     (unpacks to /opt/rae-pi)
#   .cache/rae-pi-<label>-linux-<arch>.json       build manifest
#
#   backends/pi/build-toolchain.sh [rwkv-pi dir, default ../rwkv-pi]
#
# Layout inside /opt/rae-pi (same as rwkv-pi's own `npm run start:source`):
#   bin/node            Node >= 22.19 (rwkv-pi engines), glibc build
#   dist/               rwkv-pi compiled from its git HEAD into a temp dir
#                       (the checkout's own dist/ is untracked and may be stale;
#                       it is never touched)
#   node_modules/       rwkv-pi's installed dependencies
#   pi-source/          the pinned Pi checkout (.upstream/pi, pi-source.lock.json),
#                       run through its source-resolver like run-pi-source.mjs
#   trace.mjs budget.mjs turn.mjs    this backend's helpers
#   RAE_PI_BUILD.json   label, commits, versions, file digests
# The label is rwkv-pi-<short HEAD>, with -dirty when the checkout has
# uncommitted source changes (those are compiled too and recorded as a diff).
# No .env* file is ever packed: rwkv-pi keeps engine/teacher keys there.
#
# Env: RAE_NODE=<node binary> (default: `command -v node`), must be a glibc
# linux build of Node >= 22.19 for the container arch.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/../.." && pwd)"
PI_REPO="$(cd "${1:-$HERE/../rwkv-pi}" && pwd)"
NODE="${RAE_NODE:-$(command -v node)}"
NODE="$(readlink -f "$NODE")"
ARCH="$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')"
OUT="$HERE/.cache"; mkdir -p "$OUT"

node_ver="$("$NODE" --version)"
"$NODE" -e 'const [a,b]=process.versions.node.split(".").map(Number); if(a<22||(a===22&&b<19)){console.error("need Node >= 22.19, got "+process.version);process.exit(1)}'
file "$NODE" 2>/dev/null | grep -q 'GNU/Linux' || echo "warning: $NODE may not be a glibc linux build" >&2

SRC="$PI_REPO/.upstream/pi"
[ -f "$SRC/packages/coding-agent/src/experimental/source-resolver.ts" ] || { echo "missing $SRC: run 'npm run pi:setup' in $PI_REPO" >&2; exit 1; }
[ -d "$PI_REPO/node_modules" ] || { echo "missing $PI_REPO/node_modules: run 'npm ci' in $PI_REPO" >&2; exit 1; }
lock_commit=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['commit'])" "$PI_REPO/pi-source.lock.json")
pi_commit=$(git -C "$SRC" rev-parse HEAD)
[ "$pi_commit" = "$lock_commit" ] || { echo "pi source $pi_commit != pi-source.lock.json $lock_commit" >&2; exit 1; }

head=$(git -C "$PI_REPO" rev-parse HEAD); short=$(git -C "$PI_REPO" rev-parse --short HEAD)
dirty=""; git -C "$PI_REPO" diff --quiet HEAD -- src package.json package-lock.json tsconfig.json || dirty="-dirty"
LABEL="rwkv-pi-$short$dirty"
NAME="rae-pi-$LABEL-linux-$ARCH"

STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT
R="$STAGE/rae-pi"; mkdir -p "$R/bin"
# Compile rwkv-pi's tracked sources (plus any uncommitted edits) into the stage.
( cd "$PI_REPO" && ./node_modules/.bin/tsc -p tsconfig.json --outDir "$R/dist" )
[ -f "$R/dist/extension.js" ] || { echo "tsc produced no dist/extension.js" >&2; exit 1; }
cp "$PI_REPO/package.json" "$PI_REPO/package-lock.json" "$R/"
cp "$NODE" "$R/bin/node"
tar -C "$PI_REPO" --exclude='.env*' --exclude='.cache' -cf - node_modules | tar -C "$R" -xf -
tar -C "$PI_REPO/.upstream" --exclude='.git' --exclude='node_modules' --exclude='.env*' --exclude='.pi' -cf - pi | tar -C "$R" -xf -
mv "$R/pi" "$R/pi-source"
cp "$HERE/backends/pi/trace.mjs" "$HERE/backends/pi/budget.mjs" "$HERE/backends/pi/turn.mjs" "$R/"
find "$R" -name '.env*' -print -delete | sed 's/^/removed secret-like file: /' >&2
# Absolute or escaping symlinks would break inside the container.
bad=$(find "$R" -type l -printf '%p -> %l\n' | awk -v r="$R" '$3 ~ /^\// {print}' | head -5)
[ -z "$bad" ] || { echo "absolute symlinks in toolchain:"; echo "$bad"; exit 1; } >&2

pi_ver=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$R/pi-source/packages/coding-agent/package.json")
prov_ver=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$PI_REPO/package.json")
python3 - "$R" "$LABEL" "$head" "$dirty" "$pi_ver" "$pi_commit" "$node_ver" "$prov_ver" "$PI_REPO" <<'EOF'
import hashlib, json, subprocess, sys, datetime, pathlib
r, label, head, dirty, pi_ver, pi_commit, node_ver, prov_ver, repo = sys.argv[1:]
def digest(p):
    h = hashlib.sha256()
    for f in sorted(pathlib.Path(p).rglob('*')):
        if f.is_file() and not f.is_symlink():
            h.update(str(f.relative_to(p)).encode()); h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()
diff = subprocess.run(['git', '-C', repo, 'diff', 'HEAD', '--', 'src', 'package.json', 'package-lock.json', 'tsconfig.json'],
                      capture_output=True, text=True).stdout if dirty else ''
build = {'label': label, 'provider': 'rwkv-pi', 'provider_version': prov_ver, 'provider_head': head,
         'provider_dirty': bool(dirty), 'provider_diff': diff, 'pi_version': pi_ver, 'pi_commit': pi_commit,
         'node_version': node_ver, 'built_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
         'dist_sha256': digest(f'{r}/dist'),
         'helpers_sha256': {n: hashlib.sha256(open(f'{r}/{n}', 'rb').read()).hexdigest() for n in ('trace.mjs', 'budget.mjs', 'turn.mjs')}}
json.dump(build, open(f'{r}/RAE_PI_BUILD.json', 'w'), indent=1)
EOF
# Smoke: the packed tree must start Pi from source with the provider loaded.
( cd "$STAGE" && "$R/bin/node" --import "$R/pi-source/packages/coding-agent/src/experimental/source-resolver.ts" \
    "$R/pi-source/packages/coding-agent/src/cli.ts" --version ) | tail -1 | sed 's/^/pi --version: /'
chmod -R a+rX "$R"
tar -C "$STAGE" -czf "$OUT/$NAME.tar.gz.part" rae-pi && mv "$OUT/$NAME.tar.gz.part" "$OUT/$NAME.tar.gz"
python3 - "$OUT/$NAME.tar.gz" "$R/RAE_PI_BUILD.json" "$OUT/$NAME.json" <<'EOF'
import hashlib, json, sys
tgz, build, out = sys.argv[1:]
b = json.load(open(build)); b['tarball'] = tgz.rsplit('/', 1)[1]
b['tarball_sha256'] = hashlib.sha256(open(tgz, 'rb').read()).hexdigest()
json.dump(b, open(out, 'w'), indent=1)
EOF
ls -lh "$OUT/$NAME.tar.gz"
echo "label $LABEL"
