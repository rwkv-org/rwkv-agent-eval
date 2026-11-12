# Sourced by eval-run.sh and calibrate.sh: pick the agent backend.
#
#   BACKEND=dsh (default)  DSH + dsh-rwkv-plugin   probe tasks/env-grep-probe
#   BACKEND=pi             Pi + rwkv-pi            probe tasks/env-pi-probe
#
# Needs URL (the engine as the Harbor host reaches it). CONTAINER_URL is the engine
# as task containers reach it: both harnesses run inside the container, so the
# default (URL) only works when URL is not a loopback address. RWKV_API_KEY (host
# env) is the engine credential if it has one. PI_LABEL picks a Pi toolchain other
# than ../rwkv-pi HEAD.
# Sets AGENT, MOUNTS, PROBE, AK (array of --ak args).
BACKEND="${BACKEND:-dsh}"
case "$BACKEND" in
  dsh)
    AGENT=backends.dsh.harbor_agent:DshRwkv
    PROBE=tasks/env-grep-probe
    MOUNTS=$(scripts/prepare-toolchain.sh)
    AK=(--ak rwkv_url="$URL")
    ;;
  pi)
    AGENT=backends.pi.harbor_agent:PiRwkv
    PROBE=tasks/env-pi-probe
    PI_LABEL="${PI_LABEL:-$(scripts/pi-label.sh)}"
    MOUNTS=$(scripts/prepare-toolchain.sh pi "$PI_LABEL")
    AK=(--ak rwkv_url="$URL" --ak pi_label="$PI_LABEL")
    ;;
  *) echo "BACKEND must be dsh or pi, got $BACKEND" >&2; exit 1;;
esac
[ -n "${CONTAINER_URL:-}" ] && AK+=(--ak container_url="$CONTAINER_URL")
case "${CONTAINER_URL:-$URL}" in
  *://127.*|*://localhost*) echo "the agent runs inside the task container: set CONTAINER_URL (e.g. http://172.17.0.1:<port>, see scripts/engine-bridge.py)" >&2; exit 1;;
esac
