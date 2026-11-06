#!/usr/bin/env bash
# Start a Codex review for each batch as soon as its generation run is done (<batch>.log exists).
# The old-* reviews (batch-1 cases, report only) start right away. Exits when every review has started.
cd "$(dirname "$0")"
REPO=$(cd ../.. && pwd)
start() {  # $1 = batch
  nohup codex exec -m gpt-6.1-sol -s workspace-write -c sandbox_workspace_write.network_access=true \
    -c model_reasoning_effort=high -C "$REPO" --output-last-message "$PWD/$1.review.log" - < "$1.reviewprompt" > "$1.review.err" 2>&1 &
  echo "$(date +%T) review $1 pid $!"
}
while :; do
  left=0
  for rp in *.reviewprompt; do
    k=${rp%.reviewprompt}
    [ -f "$k.review.err" ] && continue
    if [[ $k == old-* ]] || [ -f "$k.log" ]; then start "$k"; else left=$((left+1)); fi
  done
  [ $left -eq 0 ] && break
  sleep 60
done
echo "all reviews started"
