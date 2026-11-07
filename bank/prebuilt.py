#!/usr/bin/env python3
"""Point bank tasks at the shared prebuilt image instead of a per-task build.

    python3 bank/prebuilt.py build/new-v2 build/candidates tasks   # task dirs or dirs of tasks

A bank task's Dockerfile is always the same template (FROM python:3.12-slim,
WORKDIR /app, COPY workspace/ /app/, optionally turns.json / web.json into
/rae). Building it once per task cost minutes on a fresh host and serialized
`docker compose up` at high concurrency. A converted task keeps its Dockerfile
and docker-compose.yaml (the bridge network still applies; `harbor run
--force-build` still builds the old way) and gains

    [environment]
    docker_image = "rae-eval-base:py312-slim"

so Harbor starts the shared image (scripts/prepare-base-image.sh) without a
build. The agent then copies environment/workspace into /app and reads
turns.json / web.json on the host, so they never enter the container.

Tasks with any other Dockerfile (OSS tasks) are left alone. Idempotent.
"""
import sys
from pathlib import Path

BASE_IMAGE = 'rae-eval-base:py312-slim'
TEMPLATE = {'FROM python:3.12-slim', 'WORKDIR /app', 'COPY workspace/ /app/',
            'COPY turns.json /rae/turns.json', 'COPY web.json /rae/web.json'}
SECTION = f'\n[environment]\ndocker_image = "{BASE_IMAGE}"\n'


def is_template(dockerfile: Path) -> bool:
    lines = [l.strip() for l in dockerfile.read_text().splitlines() if l.strip()]
    return lines[:3] == ['FROM python:3.12-slim', 'WORKDIR /app', 'COPY workspace/ /app/'] and set(lines) <= TEMPLATE


def convert(task: Path) -> str:
    """'converted', 'already' or 'skipped'."""
    toml = task / 'task.toml'
    dockerfile = task / 'environment' / 'Dockerfile'
    if not toml.is_file() or not dockerfile.is_file() or not is_template(dockerfile):
        return 'skipped'
    text = toml.read_text()
    if '[environment]' in text:
        return 'already' if f'docker_image = "{BASE_IMAGE}"' in text else 'skipped'
    toml.write_text(text.rstrip('\n') + '\n' + SECTION)
    return 'converted'


def tasks_in(path: Path):
    if (path / 'task.toml').is_file():
        yield path
    else:
        yield from sorted(p for p in path.iterdir() if (p / 'task.toml').is_file())


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    counts = {'converted': 0, 'already': 0, 'skipped': 0}
    for arg in sys.argv[1:]:
        for task in tasks_in(Path(arg)):
            counts[convert(task)] += 1
    print(' '.join(f'{k} {v}' for k, v in counts.items()))


if __name__ == '__main__':
    main()
