# 0xchou00 — Lightweight Security Detection Tool

<p align="center">
  <img src="https://github.com/0xchou00/0xchou00-SEIM/blob/main/media/0xchou00_banner.svg?raw=1" alt="0xchou00 banner" width="100%">
</p>

`0xchou00` is a single-node security detection tool for SSH and web telemetry. It is built for direct inspection: a local agent or API ingests log lines, the backend normalizes them, applies enrichment, runs detector logic, stores events and alerts in SQLite, seals records into a hash chain, and exposes the result through FastAPI and a polling dashboard.

## Scope

This repository is a lightweight detection tool:

- one node
- one SQLite database
- one FastAPI service
- one optional local agent

It is not trying to be:

- a distributed SIEM
- a log lake
- an endpoint security suite
- a managed SOC service

## Implemented capabilities

- SSH brute-force detection with a sliding authentication-failure window
- Web scanning detection based on request rate, error ratio, sensitive path access, and scanner user agents
- YAML-driven detector rules in `rules/default_rules.yml`
- Frequency anomaly detection using rolling buckets
- IP enrichment with local GeoIP support, optional AbuseIPDB checks, and a static blacklist fallback
- Alert correlation using `rules/correlation_rules.yml`
- Hash-chained event and alert integrity verification
- API-key RBAC for viewer, analyst, and admin roles
- Local tailing agent for `/var/log/auth.log` and `/var/log/nginx/access.log`

## Processing path

```text
agent/api -> normalize -> enrich -> detect -> correlate -> sqlite -> integrity chain -> api -> dashboard
```

## Quick start

```bash
git clone https://github.com/0xchou00/0xchou00-SEIM.git
cd 0xchou00-SEIM/siem-project
chmod +x install.sh
./install.sh
sudo systemctl start 0xchou00.service
sudo systemctl start 0xchou00-agent.service
```

Useful endpoints:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/docs`

Default test API keys:

- viewer: `siem-viewer-dev-key`
- analyst: `siem-analyst-dev-key`

## Minimal verification flow

Health:

```bash
curl http://127.0.0.1:8000/health
```

Inject failed SSH logins:

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

Read alerts:

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Read enriched logs:

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Verify integrity:

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: siem-viewer-dev-key"
```

## Main interfaces

- `POST /ingest` accepts batches of SSH or web log lines
- `GET /logs` returns normalized and enriched events
- `GET /alerts` returns detector and correlation alerts from the same store
- `GET /integrity/verify` validates the hash chain
- `agent/agent.py` tails local log files and forwards batches to `/ingest`

## Design choices

- SQLite keeps the tool easy to run and inspect on one host
- GeoIP is local-first so enrichment can work without outbound calls
- Threat-intelligence lookups are cached and refreshed asynchronously so ingestion does not block on external APIs
- Correlation is rule-driven and stored as ordinary alerts so the dashboard and API do not need a separate query path

## Documents

- `ARCHITECTURE.md`
- `AGENT.md`
- `ENRICHMENT.md`
- `CORRELATION.md`
- `SECURITY.md`
- `TESTING.md`
- `docs/0xchou00_detection_tool.pdf`

## Current limits

- supported raw sources are SSH and web access logs
- GeoIP depends on a local MaxMind-compatible database if geographic context is required
- AbuseIPDB enrichment is optional and cached, so first-seen IPs may only have local context
- the dashboard uses polling instead of WebSockets
- storage remains single-node SQLite by design
