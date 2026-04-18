# DETECTION

`0xchou00 — Lightweight Security Detection Tool`

## Detector set

The tool ships four event-level detectors and one post-alert correlation stage.

Event-level detectors run inside `backend/app/detection/engine.py` in this order:

1. `brute_force`
2. `suspicious_ip`
3. `yaml_rules`
4. `anomaly_frequency`

Order matters only where detector state is shared with the same event stream. None of these detectors depend on alerts from earlier detectors in the same pass; correlation is the only stage that consumes alert output.

## SSH brute-force detector

Implementation:
- `backend/app/detection/brute_force.py`

### Logic

The detector processes only:

- `source_type == "ssh"`
- `event_type == "authentication_failure"`
- events with a populated `source_ip`

For each source IP it maintains a deque of failure timestamps. On every event:

1. append the new timestamp
2. drop entries older than `window_seconds`
3. count remaining failures
4. emit an alert when count crosses the configured threshold and the count is different from the last alerted count

Default thresholds from `PipelineConfig`:

- `failure_threshold = 5`
- `window_seconds = 60`
- `critical_multiplier = 3`

### Severity policy

Severity is raised to `critical` when any of the following holds:

- the event is already marked `is_malicious`
- `reputation_score >= 75`
- failure count reaches `failure_threshold * critical_multiplier`

Otherwise the detector emits `high`.

### Why this shape

- Failed SSH attempts are sparse, discrete events; a count-based sliding window is enough.
- Deduping on the last alerted count prevents repeated identical alerts during the same burst.
- The detector stays keyed by source IP rather than username because the operational question is hostile origin, not account enumeration statistics.

## Suspicious web IP detector

Implementation:
- `backend/app/detection/suspicious_ip.py`

### Scope

The detector processes only:

- `source_type in {"apache", "nginx", "web"}`
- `event_type == "http_request"`
- events with a populated `source_ip`

### Sub-detectors

#### 1. Request-rate detector

Maintains a deque of timestamps per source IP.

Default settings:

- `request_rate_threshold = 120`
- `request_rate_window_seconds = 60`

An alert is emitted when request count inside the window meets or exceeds the threshold.

Deduping:
- one active alert key per `(source_ip, "request_rate")`
- the key is cleared when traffic falls back below threshold

Why:
- high-rate scans and brute enumeration attempts show up as density before they show up as specific payload signatures

#### 2. Error-ratio detector

Maintains a deque of `(timestamp, http_status)` tuples per source IP.

Default settings:

- `error_ratio_threshold = 0.5`
- `error_ratio_min_requests = 10`

An alert is emitted when:

- request volume is high enough to avoid small-sample noise
- at least half of the responses are `>= 400`

Why:
- scanners and forced-browsing activity often generate more misses than normal user traffic
- the minimum request gate avoids flagging a single 404 or a small admin mistake

#### 3. Sensitive-path detector

Matches requests for known paths that rarely belong in routine traffic:

- `/.env`
- `/.git/config`
- `/wp-admin`
- `/wp-login.php`
- `/phpmyadmin`
- `/admin`
- `/backup`
- `/config.php`
- `/xmlrpc.php`

Deduping:
- one alert per `(source_ip, sensitive_path)`

Why:
- some probes are operationally important even at low volume
- relying only on request-rate logic would miss low-and-slow reconnaissance

### Severity policy

- request-rate alerts become `critical` if the IP is already marked malicious, otherwise `high`
- error-ratio alerts become `high` if malicious, otherwise `medium`
- sensitive-path alerts become `high` if malicious, otherwise `medium`

This preserves the behavioral signal while allowing enrichment to bias triage.

## YAML rules engine

Implementation:
- `backend/app/detection/yaml_rules.py`
- rules file: `rules/default_rules.yml`

### Rule types

The engine supports:

- direct field matching
- aggregated count-based matching over a time window

Each rule may constrain:

- `source_type`
- `event_type`
- arbitrary field matches through `match`
- optional `aggregation`

Supported match modes:

- exact string comparison
- `contains`
- `regex`

### Aggregation behavior

Aggregation rules define:

- `group_by`
- `window_seconds`
- `threshold`

For each matching event, the engine:

1. resolves the group key from the event
2. appends the event timestamp to a per-rule, per-group deque
3. prunes timestamps outside the window
4. emits an alert when count reaches threshold
5. dedupes by `(rule_id, group, time_bucket)`

### Why this engine exists next to code detectors

- Code detectors are better for stateful logic with multiple thresholds.
- YAML rules are better for fast iteration on direct matches and simple aggregations.
- Keeping both paths allows the tool to stay small without baking every operational rule into Python.

The rules engine is intentionally constrained. It does not attempt full Sigma compatibility or a generic query language.

## Frequency anomaly detector

Implementation:
- `backend/app/detection/anomaly.py`

### Logic

The detector keys state by:

- `source_type`
- `source_ip`

For each key it tracks:

- current bucket count
- a fixed-length history of prior bucket counts

Default configuration:

- `window_seconds = 60`
- `baseline_windows = 5`
- `min_events = 12`
- `spike_multiplier = 3.0`

Evaluation flow:

1. map the event timestamp into a fixed bucket
2. when the bucket changes, push the finished bucket count into history
3. increment the current bucket count
4. wait until `baseline_windows` of history exist
5. compute `baseline_average = mean(history)`
6. compute `threshold = max(min_events, baseline_average * spike_multiplier)`
7. emit one alert per bucket when current count crosses threshold

### Why this model

- It is transparent. Operators can reconstruct the baseline from stored events.
- It avoids fake “AI” language; this is deterministic burst detection.
- The minimum event floor prevents a low baseline from generating alerts on trivial changes.
- Keying by source type and IP preserves operational meaning. A burst from one IP should not be normalized away by unrelated traffic.

## Correlation boundary

Correlation is not an event detector. It runs after detector alerts are stored and looks for combinations defined in `rules/correlation_rules.yml`.

This separation is intentional:

- event detectors answer “what happened on this source right now?”
- correlation answers “what sequence of alerts happened close together?”

That keeps event logic simple and prevents the per-event detection path from turning into an ad hoc historical query engine.
