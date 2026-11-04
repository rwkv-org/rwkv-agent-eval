#!/usr/bin/env bash
# The oracle stands in for an agent, so it writes the final message itself.
mkdir -p /logs/agent
date -u +%H:%M > /logs/agent/final.txt
