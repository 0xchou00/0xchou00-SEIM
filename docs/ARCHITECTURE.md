# ARCHITECTURE

`0xchou00 — Lightweight Security Detection Tool`

## Runtime pipeline

```text
raw logs
  -> normalization
  -> enrichment
  -> detection
  -> correlation
  -> storage
  -> API
```

This ordering is intentional.

- Normalization runs first so every downstream stage consumes the same event schema instead of reparsing source-specific text.
- Enrichment runs before detection so severity decisions can use country, blacklist status, and cached reputation context.
- Correlation runs after event detectors because it operates on stored alerts, not raw events.
- Storage happens for both events and alerts before the API exposes them, so every operator-visible record is queryable and integrity-tracked.

## Data flow

### 1. Ingress

Two entry paths feed the same backend logic:

- `POST /ingest` accepts explicit batches of SSH or web log lines.
- `agent/agent.py` tails local files and forwards batches to `POST /ingest`.

The API accepts the source type and a list of raw lines. Source typing is explicit because the parser path is source-aware and does not attempt format autodetection.

### 2. Normalization

`backend/app/ingestion/normalizer.py` converts raw lines into `LogEvent` records.

Current supported families:

- SSH authentication logs
- Apache or Nginx access logs

Normalization produces a stable event shape with fields such as:

- `timestamp`
- `source_type`
- `event_type`
- `source_ip`
- `username`
- `process`
- `http_method`
- `http_path`
- `http_status`
- `http_user_agent`
- `raw_message`

Events that do not parse cleanly are dropped before enrichment. The pipeline does not store partially parsed records because downstream detectors depend on typed fields rather than raw-text heuristics.

### 3. Enrichment

`backend/app/enrichment/ip_enricher.py` augments parsed events using source IP context.

The enrichment order is:

1. static blacklist
2. local or reserved address handling
3. local GeoIP if a MaxMind-compatible database exists
4. cached external reputation, with background refresh when AbuseIPDB is configured

Enrichment fields are written directly onto the event:

- `country`
- `is_malicious`
- `reputation_score`
- `enrichment_source`

The pipeline is designed so enrichment failure does not block ingestion. If external reputation is unavailable, the event still proceeds with local context only.

### 4. Detection

`backend/app/detection/engine.py` applies the event to the in-process detector set.

Current detectors:

- `brute_force`
- `suspicious_ip`
- `yaml_rules`
- `anomaly_frequency`

The ingestion service reuses a cached pipeline instance for the default runtime path. That preserves detector state across API calls, which is required for sliding windows and baseline history.

### 5. Correlation

`backend/app/services/correlation.py` evaluates newly created detector alerts against `rules/correlation_rules.yml`.

Correlation does not inspect raw logs. It queries recent detector alerts from SQLite and emits a derived alert only when a rule-specific combination appears inside the configured window. Correlated alerts are stored in the same `alerts` table with:

- `detector = correlation`
- `alert_kind = correlation`
- `correlation_rule_id`
- `correlation_fingerprint`

### 6. Storage and integrity

`backend/app/storage/sqlite.py` owns the persistence layer.

Core tables:

- `logs`
- `alerts`
- `api_keys`
- `enrichment_cache`
- `chain_entries`

`backend/app/services/integrity.py` appends every stored event and alert to `chain_entries`. Integrity verification recomputes the payload hashes and replays the chain in sequence.

### 7. API exposure

`backend/app/api/routes.py` exposes:

- `POST /ingest`
- `GET /logs`
- `GET /alerts`
- `GET /health`
- `GET /integrity/verify`

The API is backed directly by SQLite queries. There is no separate query index, queue, or streaming tier.

## Module boundaries

### `backend/app/ingestion`

Responsibility:
- parse supported log formats into typed events

Does not:
- enrich IPs
- persist records
- run detectors

### `backend/app/enrichment`

Responsibility:
- attach IP context without changing event semantics

Does not:
- emit alerts
- mutate storage schema outside enrichment fields

### `backend/app/detection`

Responsibility:
- produce first-order alerts from individual events and detector state

Does not:
- query historical alerts from storage
- create multi-step attack conclusions

### `backend/app/services/correlation.py`

Responsibility:
- create higher-confidence alerts from combinations of detector alerts

Does not:
- parse raw logs
- compute first-order detections directly from events

### `backend/app/storage`

Responsibility:
- schema initialization
- compatibility migrations
- persistence and retrieval

Does not:
- make detection decisions

### `agent`

Responsibility:
- tail local files
- preserve offsets
- batch and retry ingestion requests

Does not:
- normalize locally
- perform enrichment or detection locally

## Design constraints

- Single-node execution is a hard boundary, not an incidental limitation.
- SQLite is the system of record for both events and alerts.
- The in-process detector state is part of the runtime model. Restarting the service resets rolling windows and anomaly baselines.
- The web UI is a consumer of the API, not a separate application tier.
