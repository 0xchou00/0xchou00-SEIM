# 0xchou00 — Lightweight Security Detection Tool

`Local logs. Typed events. Bounded detections.`

`0xchou00` is a single-node security detection tool for SSH and web telemetry.
It ingests raw lines through an API or local agent, normalizes them into one event schema, enriches source IP context, and runs stateful detectors plus alert correlation.
Events and alerts are stored in SQLite and sealed into a hash-linked integrity chain.
The operating model is intentionally narrow: one host, one database, one inspectable workflow, no external data stack required.

## Repository layout

```text
backend/    FastAPI API, normalization, enrichment, detection, correlation, storage
agent/      Local tailing agent for auth.log and nginx access logs
docs/       Technical references and the PDF paper
scripts/    Installation, smoke tests, systemd units, and attack simulation helpers
web/        React website for public-facing documentation and positioning
rules/      YAML detection rules, correlation rules, and local blacklist data
lab/        Docker-based attack lab
```

## Quick start

```bash
git clone https://github.com/0xchou00/0xchou00-SEIM.git
cd 0xchou00-SEIM
chmod +x scripts/install.sh
./scripts/install.sh
sudo systemctl start 0xchou00.service
sudo systemctl start 0xchou00-agent.service
```

Backend endpoints:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

Default API keys:

- viewer: `siem-viewer-dev-key`
- analyst: `siem-analyst-dev-key`
- admin: `siem-admin-dev-key`

## Minimal verification

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/alerts?since_minutes=60" -H "X-API-Key: siem-viewer-dev-key"
curl "http://127.0.0.1:8000/logs?since_minutes=60" -H "X-API-Key: siem-viewer-dev-key"
curl http://127.0.0.1:8000/integrity/verify -H "X-API-Key: siem-viewer-dev-key"
```

## Main capabilities

- SSH brute-force detection with a sliding failure window
- suspicious web activity detection for rate, error ratio, and sensitive paths
- YAML-driven rules and simple aggregation-based detections
- frequency anomaly detection with rolling per-source baselines
- IP enrichment with local blacklist, optional GeoIP, and optional AbuseIPDB cache
- alert correlation through YAML correlation rules
- hash-linked integrity verification for stored logs and alerts
- local ingestion agent for `/var/log/auth.log` and `/var/log/nginx/access.log`

## Documentation

- `docs/ARCHITECTURE.md`
- `docs/DETECTION.md`
- `docs/AGENT.md`
- `docs/TESTING.md`
- `docs/LAB.md`
- `docs/LIMITATIONS.md`
- `docs/ENRICHMENT.md`
- `docs/CORRELATION.md`
- `docs/SECURITY.md`
- `docs/0xchou00_detection_tool.pdf`

## Web app

The React site lives in `web/` and is intended to be deployed separately with Vercel or Netlify.

## Operating limits

- storage is single-node SQLite by design
- supported raw sources are SSH and web access logs
- there is no distributed ingestion or shared detector state
- the backend exposes an API only; the website is a separate deploy target
