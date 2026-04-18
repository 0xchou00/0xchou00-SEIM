from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient


def main() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    backend_dir = root_dir / "backend"
    db_path = backend_dir / "data" / "smoke-test.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    os.environ["SIEM_DB_PATH"] = str(db_path)
    os.environ["SIEM_RULES_PATH"] = str(root_dir / "rules" / "default_rules.yml")
    os.environ["SIEM_CORRELATION_RULES_PATH"] = str(root_dir / "rules" / "correlation_rules.yml")
    os.environ["SIEM_STATIC_BLACKLIST_PATH"] = str(root_dir / "rules" / "static_blacklist.txt")

    import sys

    sys.path.insert(0, str(backend_dir))
    from main import app

    analyst_headers = {"X-API-Key": "siem-analyst-dev-key"}
    viewer_headers = {"X-API-Key": "siem-viewer-dev-key"}

    ssh_batch = [
        "Apr 18 10:00:00 sensor sshd[1001]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
        "Apr 18 10:00:05 sensor sshd[1002]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
        "Apr 18 10:00:10 sensor sshd[1003]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
        "Apr 18 10:00:15 sensor sshd[1004]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
        "Apr 18 10:00:20 sensor sshd[1005]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
    ]
    web_batch = [
        '203.0.113.50 - - [18/Apr/2026:10:01:00 +0000] "GET /.env HTTP/1.1" 404 123 "-" "curl/8.0"',
        '203.0.113.50 - - [18/Apr/2026:10:01:01 +0000] "GET /admin HTTP/1.1" 404 123 "-" "curl/8.0"',
    ]

    with TestClient(app) as client:
        ssh_response = client.post(
            "/ingest",
            json={"source_type": "ssh", "lines": ssh_batch},
            headers=analyst_headers,
        )
        web_response = client.post(
            "/ingest",
            json={"source_type": "nginx", "lines": web_batch},
            headers=analyst_headers,
        )
        alerts_response = client.get("/alerts", headers=viewer_headers)
        logs_response = client.get("/logs", headers=viewer_headers)
        verify_response = client.get("/integrity/verify", headers=viewer_headers)

    assert ssh_response.status_code == 200, ssh_response.text
    assert web_response.status_code == 200, web_response.text
    assert alerts_response.status_code == 200, alerts_response.text
    assert logs_response.status_code == 200, logs_response.text
    assert verify_response.status_code == 200, verify_response.text

    alerts = alerts_response.json()["items"]
    logs = logs_response.json()["items"]
    verify = verify_response.json()

    assert any(item["detector"] == "brute_force" for item in alerts)
    assert any(item["detector"] == "correlation" for item in alerts)
    assert any(item.get("is_malicious") for item in logs)
    assert verify["valid"] is True

    print("smoke test passed")


if __name__ == "__main__":
    main()
