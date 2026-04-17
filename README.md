# 0xchou00 platform

<p align="center">
  <img src="https://github.com/0xchou00/0xchou00-SEIM/blob/main/media/0xchou00_banner.svg?raw=1" alt="0xchou00 banner" width="100%">
</p>

`0xchou00 platform` is a local-first detection stack for SSH and web logs. The public version is intentionally small: it parses raw log lines, turns them into a stable event schema, runs a few high-signal detectors, stores the results in SQLite, and exposes the pipeline through a FastAPI backend and a browser dashboard.

This repository is meant to be tested, not just read.

## What is implemented

- SSH brute-force detection with sliding-window counting
- Suspicious web activity detection based on request rate, error ratio, and sensitive path access
- YAML-driven detection rules without changing Python code
- Frequency-based anomaly detection using rolling event buckets
- Tamper-evident hash chaining for stored logs and alerts
- Role-based API access with viewer and analyst test keys
- Live dashboard backed by polling, not screenshots or mock data

## Execution path

```text
raw logs -> normalizer -> detection engine -> sqlite -> integrity chain -> API -> dashboard
```

## Public scope

What this repo is:

- a single-node security telemetry and detection platform
- easy to install on Linux
- easy to validate with curl and sample attack traffic

What this repo is not:

- a distributed SIEM cluster
- a full syslog infrastructure
- a managed SOC product
- a fake AI analytics demo

## Quick start

```bash
git clone https://github.com/0xchou00/0xchou00-SEIM.git
cd 0xchou00-SEIM/siem-project
chmod +x install.sh
./install.sh
sudo systemctl start 0xchou00.service
sudo systemctl status 0xchou00.service
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/docs`

Default test API keys:

- viewer: `siem-viewer-dev-key`
- analyst: `siem-analyst-dev-key`

## Minimal test flow

Check service health:

```bash
curl http://127.0.0.1:8000/health
```

Ingest five failed SSH logins from one source:

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

Read normalized logs:

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Verify integrity state:

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: siem-viewer-dev-key"
```

## Main routes

- `GET /health` returns service status plus log and alert counts
- `POST /ingest` accepts raw lines for supported source types
- `GET /alerts` filters stored alerts
- `GET /logs` filters stored normalized events
- `GET /integrity/verify` checks the hash chain
- `GET /dashboard` opens the operator view

## Detection model

The public version ships four detection layers:

1. `BruteForceDetector`
Counts failed SSH authentications per source IP in a 60-second window. Alerts at 5 failures. Escalates severity when the count keeps climbing.

2. `SuspiciousIPDetector`
Looks for noisy web clients: high request rate, high HTTP error ratio, and requests to sensitive paths such as `/.env` or `/.git/config`.

3. `YAMLRuleDetector`
Loads custom rules from `rules/default_rules.yml`. Supports direct field matching, substring checks, regex matching, and aggregation windows.

4. `FrequencyAnomalyDetector`
Builds a short baseline from recent windows and alerts when current activity spikes above that baseline. This is threshold-based anomaly detection, not a machine-learning claim.

## Storage model

- logs are stored in `logs`
- alerts are stored in `alerts`
- API keys are stored in `api_keys`
- hash-chain state is stored in `chain_entries`

Default database path:

- `backend/data/0xchou00.db`

SQLite was chosen here for one reason: the product should be runnable by one person on one machine without extra infrastructure.

## Files worth reading

- `ARCHITECTURE.md` for the file tree and module boundaries
- `TESTING.md` for reproducible attack simulations
- `rules/default_rules.yml` for public detection content
- `docs/0xchou00_public_platform_article.tex` for the technical article version

## Current limits

- supported raw sources are SSH and web access logs
- the dashboard uses polling instead of WebSockets
- storage is single-node SQLite
- detections are explainable and inspectable, but intentionally narrow

Those are design constraints, not hidden gaps.
