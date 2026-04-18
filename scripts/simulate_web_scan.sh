#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/lab/docker-compose.yml"
SCENARIO="${1:-scan}"
FLOOD_COUNT="${FLOOD_COUNT:-140}"

case "$SCENARIO" in
  scan)
    docker compose -f "$COMPOSE_FILE" exec -T attacker bash -lc "
for path in /.env /.git/config /admin /phpmyadmin /wp-login.php; do
  curl -s -o /dev/null -A 'curl/8.0' http://victim\$path || true
  sleep 1
done
"
    echo "Directory scan simulation sent."
    ;;
  flood)
    docker compose -f "$COMPOSE_FILE" exec -T attacker bash -lc "
for request_id in \$(seq 1 $FLOOD_COUNT); do
  curl -s -o /dev/null -A 'curl/8.0' http://victim/healthcheck?request=\${request_id} || true
done
"
    echo "High request flood simulation sent."
    ;;
  *)
    echo "Usage: $0 [scan|flood]" >&2
    exit 1
    ;;
esac

echo "Query alerts with:"
echo "curl 'http://127.0.0.1:8000/alerts?since_minutes=15' -H 'X-API-Key: siem-viewer-dev-key'"
