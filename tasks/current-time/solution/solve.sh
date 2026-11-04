#!/usr/bin/env bash
mkdir -p "${RAE_LOGS_DIR:-/logs}/agent"
date -u +%H:%M > "${RAE_LOGS_DIR:-/logs}/agent/final.txt"
