#!/usr/bin/env python3
"""Copy downloaded Harbor datasets into one flat, run-ready dir: build/oss/.

    python3 bank/prepare_oss.py [--datasets .cache/datasets] [--out build/oss]

Per task: the dir is named <dataset>__<task>; environment/docker-compose.yaml
puts the container on Docker's default bridge (like our own tasks: a compose
network per trial exhausts the address pools at high concurrency); [metadata]
gains block (eval capability block) and split = "oss", so scores sit next to
the in-distribution blocks on the dashboard. A task that already ships its own
compose file is skipped and listed (merging it needs a look).
"""
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# dataset -> (eval block, keep(task name) -> bool)
DATASETS = {
    'humanevalfix': ('code-fix-oss', lambda n: True),
    'quixbugs': ('code-fix-oss', lambda n: 'python' in n),  # the Python half (datasets.lock.toml)
    'openthoughts-tblite': ('terminal', lambda n: True),
    'terminal-bench-sample': ('terminal', lambda n: True),
}
COMPOSE = 'services:\n  main:\n    network_mode: bridge\n'


def tag(toml, block, dataset):
    add = f'block = "{block}"\nsplit = "oss"\nsource_dataset = "{dataset}"\n'
    if re.search(r'^\[metadata\]\s*$', toml, re.M):
        toml = re.sub(r'^(block|split|source_dataset)\s*=.*\n', '', toml, flags=re.M)
        return re.sub(r'^\[metadata\]\s*$', '[metadata]\n' + add.rstrip('\n'), toml, count=1, flags=re.M)
    return toml.rstrip('\n') + '\n\n[metadata]\n' + add


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--datasets', default=str(ROOT / '.cache' / 'datasets'))
    ap.add_argument('--out', default=str(ROOT / 'build' / 'oss'))
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    counts, skipped = {}, []
    for ds, (block, keep) in DATASETS.items():
        for toml in sorted(Path(a.datasets, ds).rglob('task.toml')):
            src = toml.parent
            if not keep(src.name):
                continue
            env = src / 'environment'
            if any((env / n).exists() for n in ('docker-compose.yaml', 'docker-compose.yml', 'compose.yaml')):
                skipped.append(f'{ds}/{src.name}')
                continue
            dst = out / f'{ds}__{src.name}'
            shutil.copytree(src, dst)
            (dst / 'environment').mkdir(exist_ok=True)
            (dst / 'environment' / 'docker-compose.yaml').write_text(COMPOSE)
            (dst / 'task.toml').write_text(tag((dst / 'task.toml').read_text(), block, ds))
            counts[ds] = counts.get(ds, 0) + 1
    print(f'wrote {sum(counts.values())} tasks to {out}: {counts}')
    if skipped:
        print(f'skipped {len(skipped)} with their own compose file: {skipped[:10]}')


if __name__ == '__main__':
    main()
