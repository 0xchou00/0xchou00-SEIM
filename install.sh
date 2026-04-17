#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$PROJECT_ROOT/.venv"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="0xchou00.service"
ENV_FILE="$PROJECT_ROOT/.env"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is required but was not found."
  exit 1
fi

echo "[1/6] Creating Python virtual environment"
python3 -m venv "$VENV_DIR"

echo "[2/6] Installing Python dependencies"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PROJECT_ROOT/requirements.txt"

echo "[3/6] Preparing runtime directories"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$BACKEND_DIR/data"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[4/6] Creating default environment file"
  cat > "$ENV_FILE" <<EOF
SIEM_DB_PATH=$BACKEND_DIR/data/siem.db
SIEM_ADMIN_API_KEY=siem-admin-dev-key
SIEM_ANALYST_API_KEY=siem-analyst-dev-key
SIEM_VIEWER_API_KEY=siem-viewer-dev-key
EOF
else
  echo "[4/6] Using existing environment file at $ENV_FILE"
fi

echo "[5/6] Installing systemd unit"
sudo cp "$PROJECT_ROOT/deploy/$SERVICE_NAME" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo sed -i "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo sed -i "s|__BACKEND_DIR__|$BACKEND_DIR|g" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo "[6/6] Setup complete"
echo
echo "Next steps:"
echo "  1. Review $ENV_FILE"
echo "  2. Start the service: sudo systemctl start $SERVICE_NAME"
echo "  3. Check status:       sudo systemctl status $SERVICE_NAME"
echo "  4. Open landing page:  http://127.0.0.1:8000/"
echo "  5. Open dashboard:     http://127.0.0.1:8000/dashboard"
