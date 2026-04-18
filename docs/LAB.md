# LAB

`0xchou00 — Lightweight Security Detection Tool`

## Purpose

The lab is a local three-container environment for exercising the shipped detection logic against real service logs.

Containers:

- `attacker`
  Linux container used to run SSH login attempts and HTTP probes
- `victim`
  Debian-based container running OpenSSH, Nginx, and rsyslog
- `siem`
  The 0xchou00 backend and ingestion agent in one container

The victim writes authentication and web access logs into a shared Docker volume. The SIEM agent tails that volume and forwards lines into the backend through the same `POST /ingest` path used outside the lab.

## Files

- `lab/docker-compose.yml`
- `lab/attacker.Dockerfile`
- `lab/victim.Dockerfile`
- `lab/siem.Dockerfile`
- `lab/agent.config.yaml`
- `scripts/simulate_ssh_attack.sh`
- `scripts/simulate_web_scan.sh`

## Setup

From the repository root:

```bash
docker compose -f lab/docker-compose.yml build
docker compose -f lab/docker-compose.yml up -d
```

Wait for the SIEM API:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

- HTTP `200`
- JSON containing log and alert counts

## Topology

```text
attacker -> victim:ssh
attacker -> victim:http
victim -> shared volume (auth.log, nginx access.log)
siem agent -> shared volume
siem agent -> siem API /ingest
operator -> localhost:8000
```

## Scenarios

### 1. SSH brute force

Run:

```bash
chmod +x scripts/simulate_ssh_attack.sh
./scripts/simulate_ssh_attack.sh
```

What it does:

- executes repeated password-auth SSH attempts from the attacker to the victim
- uses an incorrect password for `labuser`
- causes OpenSSH failures to be written into the victim auth log

Expected alerts:

- `brute_force`
- if `203.0.113.50` or another flagged IP is used in manual injections later, severity may escalate based on enrichment

Verification:

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=15" \
  -H "X-API-Key: siem-viewer-dev-key"
```

### 2. Directory scan

Run:

```bash
chmod +x scripts/simulate_web_scan.sh
./scripts/simulate_web_scan.sh scan
```

What it does:

- requests a fixed list of sensitive paths on the victim web server
- uses `curl/8.0` as the user agent so the YAML scanner rule also matches

Expected alerts:

- `suspicious_ip` with `metadata.reason = sensitive_path`
- `yaml_rules` for scanning user agent matches

Verification:

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=15" \
  -H "X-API-Key: siem-viewer-dev-key"
curl "http://127.0.0.1:8000/alerts?since_minutes=15" \
  -H "X-API-Key: siem-viewer-dev-key"
```

### 3. High request flood

Run:

```bash
./scripts/simulate_web_scan.sh flood
```

What it does:

- sends a burst of repeated requests from the attacker to the victim
- drives the suspicious request-rate detector
- may also contribute to the frequency anomaly detector when enough baseline history exists

Expected alerts:

- `suspicious_ip` with `metadata.reason = request_rate`
- possibly `anomaly_frequency` after the detector has baseline windows to compare against

## Correlation scenario

To trigger correlation, run the SSH brute-force simulation first and then the directory scan within five minutes:

```bash
./scripts/simulate_ssh_attack.sh
./scripts/simulate_web_scan.sh scan
```

Expected:

- one `correlation` alert tying SSH brute-force activity and suspicious web behavior to the same source sequence when rule conditions are met

## Verification workflow

Health:

```bash
curl http://127.0.0.1:8000/health
```

Alerts:

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=15" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Logs:

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=15" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Integrity:

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: siem-viewer-dev-key"
```

Container logs:

```bash
docker compose -f lab/docker-compose.yml logs -f siem
docker compose -f lab/docker-compose.yml logs -f victim
```

## Teardown

```bash
docker compose -f lab/docker-compose.yml down -v
```

This removes the containers and the shared log volume so the lab starts clean on the next run.
