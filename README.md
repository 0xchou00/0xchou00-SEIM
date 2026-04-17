# 0xchou00 platform

![0xchou00 banner](./media/0xchou00_banner.svg)

0xchou00 platform is a lightweight SIEM demo platform for SSH and web telemetry. It ingests raw log lines, normalizes them into structured events, applies multiple detection layers, stores logs and alerts in SQLite, and verifies record integrity through a hash chain.

## What you can test

- SSH brute-force detection
- suspicious web activity detection
- YAML-based detection rules
- frequency-based anomaly detection
- tamper-evident integrity verification
- live dashboard for logs and alerts

## Architecture

```text
raw logs -> normalize -> detect -> sqlite -> integrity chain -> api -> dashboard
```

Core routes:

- `/`
  landing page
- `/dashboard`
  live operator dashboard
- `/health`
  service health
- `/ingest`
  submit log lines
- `/alerts`
  query alerts
- `/logs`
  query normalized logs
- `/integrity/verify`
  verify chain integrity

## Quick start

```bash
git clone https://github.com/0xchou00/0xchou00-SEIM.git
cd 0xchou00-SEIM/siem-project
chmod +x install.sh
./install.sh
sudo systemctl start 0xchou00.service
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/dashboard`

Default test keys:

- viewer: `siem-viewer-dev-key`
- analyst: `siem-analyst-dev-key`

## Demo commands

### Health

```bash
curl http://127.0.0.1:8000/health
```

### Ingest SSH failures

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: siem-analyst-dev-key" \
  -d '{
    "source_type": "ssh",
    "lines": [
      "Jan 15 03:21:00 web01 sshd[1001]: Failed password for root from 203.0.113.50 port 55001 ssh2",
      "Jan 15 03:21:01 web01 sshd[1002]: Failed password for root from 203.0.113.50 port 55002 ssh2",
      "Jan 15 03:21:02 web01 sshd[1003]: Failed password for root from 203.0.113.50 port 55003 ssh2",
      "Jan 15 03:21:03 web01 sshd[1004]: Failed password for root from 203.0.113.50 port 55004 ssh2",
      "Jan 15 03:21:04 web01 sshd[1005]: Failed password for root from 203.0.113.50 port 55005 ssh2"
    ]
  }'
```

### Query alerts

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

### Query logs

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

### Verify integrity

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: siem-viewer-dev-key"
```

## Files worth opening

- `ARCHITECTURE.md`
  clean file tree and module boundaries
- `TESTING.md`
  step-by-step test scenarios
- `rules/default_rules.yml`
  example YAML detection content

## Notes

- default storage path: `backend/data/0xchou00.db`
- default service name: `0xchou00.service`
- SQLite is used for easy local testing and single-node demos
