#!/usr/bin/env bash
set -euo pipefail

cd /opt/0xchou00/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
api_pid=$!

sleep 3

cd /opt/0xchou00
python agent/agent.py --config /opt/0xchou00/lab/agent.config.yaml &
agent_pid=$!

cleanup() {
  kill "${api_pid}" "${agent_pid}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

wait -n "${api_pid}" "${agent_pid}"
