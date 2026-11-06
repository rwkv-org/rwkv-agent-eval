#!/usr/bin/env bash
# Make a toolchain whose DSH code is an exact source commit, not an npm release.
#
#   backends/dsh/overlay-toolchain.sh <base toolchain .tar.gz> <dir of packed .tgz> <label>
#
# The base (build-toolchain.sh output, same DSH version line) supplies the
# install layout, third-party dependencies and native addons. Every
# @deepseek-ai/* package directory in it is replaced by the contents of the
# matching tarball from `pnpm run release:pack --family dsh` at the source
# commit; source-only packages are added beside them. Output: .cache/rae-node-<label>-linux-<arch>.tar.gz, used with
# --ak dsh_version=<label>. Prints packages found in only one of the two.
#
# Why: the training data (rwkv-agent-pipeline) ran DSH from source at a commit
# that was never published (8bd07339); the npm 0.2.2-alpha.3 differs in 111
# packages, including prompt text.
set -euo pipefail
BASE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; PACKS="$(cd "$2" && pwd)"; LABEL="$3"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ARCH="$(basename "$BASE" .tar.gz | sed 's/.*-linux-//')"
OUT="$ROOT/.cache/rae-node-$LABEL-linux-$ARCH.tar.gz"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
tar -xzf "$BASE" -C "$WORK"
python3 - "$WORK/rae-node" "$PACKS" <<'PY'
import json, sys, tarfile, shutil, io
from pathlib import Path
root, packs = Path(sys.argv[1]), Path(sys.argv[2])
installed = {}
for pj in root.rglob('package.json'):
    if pj.parent.parent.name != '@deepseek-ai' or pj.parent.parent.parent.name != 'node_modules':
        continue
    try:
        d = pj.parent.resolve()
        lst = installed.setdefault(json.loads(pj.read_text())['name'], [])
        if d not in lst:
            lst.append(d)
    except Exception:
        pass
used, replaced, added = set(), 0, []
for tgz in sorted(packs.glob('*.tgz')):
    with tarfile.open(tgz) as t:
        name = json.load(t.extractfile('package/package.json'))['name']
        for dest in installed.get(name, []):
            if dest.is_symlink() or not dest.exists():
                continue
            # Replace the package's own files; its nested node_modules (where
            # npm put its dependencies) stays.
            for child in dest.iterdir():
                if child.name == 'node_modules':
                    continue
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            for m in t.getmembers():
                if not m.name.startswith('package/') or not (m.isfile() or m.isdir()):
                    continue
                rel = m.name[len('package/'):]
                if not rel:
                    continue
                if rel == 'node_modules' or rel.startswith('node_modules/'):
                    continue
                target = dest / rel
                if m.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(t.extractfile(m).read())
                target.chmod(m.mode | 0o644)
            replaced += 1
        if name in installed:
            used.add(name)
        else:
            # Source-only package (e.g. renamed since the npm release): install it
            # next to DSH's other @deepseek-ai deps, as the source checkout had it.
            dest = root / 'lib/node_modules/@deepseek-ai/dsh/node_modules' / name
            dest.mkdir(parents=True)
            for m in t.getmembers():
                rel = m.name[len('package/'):] if m.name.startswith('package/') else ''
                if not rel or not (m.isfile() or m.isdir()):
                    continue
                target = dest / rel
                if m.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(t.extractfile(m).read())
                target.chmod(m.mode | 0o644)
            added.append(name)
for name in sorted(set(installed) - used):
    print(f'kept from npm (no source tarball): {name}')
print(f'replaced {replaced} package dirs from {len(used)} source packages; added {len(added)} source-only packages')
PY
"$WORK/rae-node/bin/node" "$WORK/rae-node/bin/dsh" --version >/dev/null 2>&1 && echo "dsh runs" || echo "WARNING: dsh --version failed on this host (fine if cross-arch)"
printf '%s\n' "$LABEL" > "$WORK/rae-node/RAE_DSH_SOURCE"
tar -czf "$OUT" -C "$WORK" rae-node
ls -lh "$OUT"
