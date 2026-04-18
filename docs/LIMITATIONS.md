# LIMITATIONS

`0xchou00 — Lightweight Security Detection Tool`

## Single-node only

The tool assumes one SQLite database and one backend process as the authoritative runtime.

Implications:

- detector state lives in process memory
- rolling windows and anomaly baselines reset on restart
- there is no shared detector state across multiple backend instances

This is a deliberate tradeoff for inspectability and low setup cost.

## No distributed ingestion

There is no queue, broker, or partitioned ingest layer.

Implications:

- ingestion throughput is bounded by one API process and one local database
- the agent posts directly to the backend instead of writing to an intermediate transport
- sustained backlog handling is limited

This keeps operations simple at the cost of horizontal scalability.

## No streaming query model

The tool does not expose a real-time streaming API.

Implications:

- the bundled operator UI polls the REST API
- there is no WebSocket feed
- alert visibility is near-real-time rather than push-driven

Polling was chosen because the backend already stores alerts durably and the target deployment model does not justify a separate streaming layer.

## Limited source coverage

Current normalization is built for:

- SSH authentication logs
- Apache or Nginx access logs

Everything else requires parser work before the rest of the pipeline can use it.

This is preferable to partial generic parsing because the shipped detectors rely on typed fields with stable semantics.

## Correlation scope is intentionally small

Correlation operates on recent alerts with YAML-defined selector logic.

Implications:

- it handles short multi-step sequences well
- it does not attempt graph analysis, campaign tracking, or long-horizon attack reconstruction

The design goal is operationally useful sequences, not a generic analytics engine.

## Enrichment is best-effort

GeoIP requires a local MaxMind-compatible database. External threat-intelligence lookups require an AbuseIPDB API key and are cached asynchronously.

Implications:

- some events will carry only local blacklist context
- first-seen public IPs may not have remote reputation immediately
- enrichment absence should be treated as “unknown,” not “benign”

This keeps ingestion responsive under constrained connectivity.

## Integrity is tamper-evidence, not tamper-prevention

The hash chain can detect mutation of stored events and alerts after the fact.

It does not:

- prevent deletion of the database by a privileged local actor
- provide external notarization
- replace off-host backups

The chain is useful for local integrity checks, not for hostile-environment non-repudiation.
