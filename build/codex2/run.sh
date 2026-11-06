#!/usr/bin/env bash
# Launch every batch prompt in this dir as its own Codex run (parallel).
#   build/codex2/run.sh [batch ...]     (default: all *.prompt without a .log)
cd "$(dirname "$0")"
REPO=$(cd ../.. && pwd)
for p in ${@:-*.prompt}; do
  k=${p%.prompt}
  [ -f "$k.log" ] && continue
  nohup codex exec -m gpt-6.1-sol -s workspace-write -c sandbox_workspace_write.network_access=true \
    -c model_reasoning_effort=high -C "$REPO" --output-last-message "$PWD/$k.log" - < "$k.prompt" > "$k.err" 2>&1 &
  echo "$k $!"
done
