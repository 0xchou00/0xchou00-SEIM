#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$PROJECT_ROOT/.venv"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="0xchou00.service"
AGENT_SERVICE_NAME="0xchou00-agent.service"
ENV_FILE="$PROJECT_ROOT/.env"
AGENT_CONFIG_FILE="$PROJECT_ROOT/agent/config.yaml"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is required but was not found."
  exit 1
fi

echo "[1/7] Creating Python virtual environment"
python3 -m venv "$VENV_DIR"

echo "[2/7] Installing Python dependencies"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PROJECT_ROOT/requirements.txt"

echo "[3/7] Preparing runtime directories"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$BACKEND_DIR/data"
mkdir -p "$PROJECT_ROOT/agent"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[4/7] Creating default environment file"
  cat > "$ENV_FILE" <<EOF
SIEM_DB_PATH=$BACKEND_DIR/data/0xchou00.db
SIEM_ADMIN_API_KEY=siem-admin-dev-key
SIEM_ANALYST_API_KEY=siem-analyst-dev-key
SIEM_VIEWER_API_KEY=siem-viewer-dev-key
EOF
else
  echo "[4/7] Using existing environment file at $ENV_FILE"
fi

if [[ ! -f "$AGENT_CONFIG_FILE" ]]; then
  echo "[5/7] Creating default agent configuration"
  cat > "$AGENT_CONFIG_FILE" <<EOF
api:
  url: "http://127.0.0.1:8000/ingest"
  api_key: "siem-analyst-dev-key"
batch:
  max_lines: 25
  flush_interval_seconds: 3
tail:
  poll_interval_seconds: 0.5
state_file: "./state.json"
sources:
  - source_type: "ssh"
    path: "/var/log/auth.log"
    start_at_end: true
  - source_type: "nginx"
    path: "/var/log/nginx/access.log"
    start_at_end: true
EOF
else
  echo "[5/7] Using existing agent configuration at $AGENT_CONFIG_FILE"
fi

echo "[6/7] Installing systemd units"
sudo cp "$PROJECT_ROOT/deploy/$SERVICE_NAME" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo cp "$PROJECT_ROOT/deploy/$AGENT_SERVICE_NAME" "$SYSTEMD_DIR/$AGENT_SERVICE_NAME"
sudo sed -i "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo sed -i "s|__BACKEND_DIR__|$BACKEND_DIR|g" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo sed -i "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" "$SYSTEMD_DIR/$AGENT_SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl enable "$AGENT_SERVICE_NAME"

echo "[7/7] Setup complete"
echo
echo "Next steps:"
echo "  1. Review $ENV_FILE"
echo "  2. Review $AGENT_CONFIG_FILE"
echo "  3. Start the tool:     sudo systemctl start $SERVICE_NAME"
echo "  4. Start the agent:    sudo systemctl start $AGENT_SERVICE_NAME"
echo "  5. Check tool status:  sudo systemctl status $SERVICE_NAME"
echo "  6. Check agent status: sudo systemctl status $AGENT_SERVICE_NAME"
echo "  7. Open dashboard:     http://127.0.0.1:8000/dashboard"
