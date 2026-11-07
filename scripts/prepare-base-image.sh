#!/usr/bin/env bash
# Build the shared bank-task image once on the Harbor host (idempotent; Docker
# reuses the cached layers). Tasks converted by bank/prebuilt.py start from it
# instead of building one image per task.
#
#   scripts/prepare-base-image.sh      prints the image id
set -euo pipefail
cd "$(dirname "$0")/.."
TAG=$(sed -n "s/^BASE_IMAGE = '\([^']*\)'.*/\1/p" bank/prebuilt.py)
docker build -q -t "$TAG" backends/base-image >/dev/null
docker image inspect "$TAG" --format '{{.Id}}'
