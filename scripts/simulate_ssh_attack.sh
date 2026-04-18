#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/lab/docker-compose.yml"
ATTEMPTS="${ATTEMPTS:-8}"
TARGET_USER="${TARGET_USER:-labuser}"
WRONG_PASSWORD="${WRONG_PASSWORD:-wrongpass}"

docker compose -f "$COMPOSE_FILE" exec -T attacker bash -lc "
for attempt in \$(seq 1 $ATTEMPTS); do
  sshpass -p '$WRONG_PASSWORD' ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o PreferredAuthentications=password \
    -o PubkeyAuthentication=no \
    -o ConnectTimeout=2 \
    ${TARGET_USER}@victim 'exit' >/dev/null 2>&1 || true
  sleep 1
done
"

echo "SSH brute-force simulation sent. Query alerts with:"
echo "curl 'http://127.0.0.1:8000/alerts?since_minutes=15' -H 'X-API-Key: siem-viewer-dev-key'"
