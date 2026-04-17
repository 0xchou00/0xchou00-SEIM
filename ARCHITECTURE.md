# 0xchou00 Detection Tool Architecture

## Overview

`0xchou00` is organized around one ingestion and analysis path:

1. collect lines through the API or the local agent
2. normalize raw text into a stable event schema
3. enrich source IPs with local or cached context
4. run detector logic
5. correlate related alerts
6. persist events and alerts in SQLite
7. seal records into a hash chain
8. expose results through the API and dashboard

## Runtime components

```text
agent -> /ingest -> normalizer -> enrichment -> detectors -> correlation
     -> sqlite logs/alerts/cache -> integrity chain -> /logs /alerts /dashboard
```

## File tree

```text
siem-project/
├── AGENT.md
├── ARCHITECTURE.md
├── CORRELATION.md
├── ENRICHMENT.md
├── README.md
├── SECURITY.md
├── TESTING.md
├── agent/
│   ├── agent.py
│   └── config.yaml
├── backend/
│   ├── main.py
│   └── app/
│       ├── api/
│       ├── core/
│       ├── detection/
│       ├── enrichment/
│       ├── ingestion/
│       ├── models/
│       ├── security/
│       ├── services/
│       └── storage/
├── deploy/
│   ├── 0xchou00.service
│   └── 0xchou00-agent.service
├── docs/
│   ├── 0xchou00_detection_tool.pdf
│   ├── 0xchou00_detection_tool.tex
│   └── 0xchou00_detection_tool_references.bib
├── frontend/
├── media/
└── rules/
    ├── correlation_rules.yml
    ├── default_rules.yml
    └── static_blacklist.txt
```

## Module responsibilities

- `agent`
  Tails local log files, batches lines, keeps byte offsets, and forwards to `/ingest`.

- `backend/app/ingestion`
  Parses supported SSH and web log formats into structured events.

- `backend/app/enrichment`
  Adds local GeoIP context, static blacklist hits, and cached threat-intelligence results.

- `backend/app/detection`
  Runs the event-level detectors: SSH brute force, suspicious web IP behavior, YAML rules, and frequency anomalies.

- `backend/app/services/correlation.py`
  Builds higher-confidence alerts from multiple detector alerts using YAML correlation rules.

- `backend/app/storage`
  Persists events, alerts, API keys, enrichment cache records, and integrity-chain entries.

- `backend/app/security`
  Applies role-ranked API-key access control.

- `frontend`
  Displays current logs and alerts from the same API the agent uses.

## Persistence model

SQLite tables:

- `logs`
  normalized and enriched events
- `alerts`
  detector alerts and correlation alerts
- `api_keys`
  local role assignments
- `enrichment_cache`
  cached threat-intelligence responses
- `chain_entries`
  tamper-evident record chain

## Operational philosophy

This tool stays intentionally small:

- no message bus
- no distributed search backend
- no cluster management
- no hidden external dependency required for the core path

The tradeoff is scale. The benefit is that the entire collection, enrichment, detection, correlation, storage, and verification path can be inspected on one machine.
