# Enrichment

## Purpose

The enrichment layer adds IP context after normalization and before detector execution. It keeps the detector code focused on behavior while still making severity decisions aware of geographic or reputation signals.

## Event fields

Each event may include:

- `country`
- `is_malicious`
- `reputation_score`
- `enrichment_source`

## Sources

### 1. Local GeoIP

If `SIEM_GEOIP_DB_PATH` points to a MaxMind-compatible database, the tool reads country information locally.

Default path:

- `data/GeoLite2-City.mmdb`

If the database is missing, the tool continues without GeoIP context.

### 2. Static blacklist

`rules/static_blacklist.txt` is checked synchronously. If the source IP is present:

- `is_malicious = true`
- `reputation_score = 100`
- `enrichment_source = static_blacklist`

This path works even without Internet access.

### 3. AbuseIPDB

If `ABUSEIPDB_API_KEY` is set, the tool schedules a background lookup for unseen public IPs.

Important design choice:

- the lookup is cached
- the request is not performed inline with event ingestion
- ingestion returns immediately with local context only

That keeps the detection path responsive even when the external service is slow or unavailable.

## Cache

Threat-intelligence results are stored in SQLite table `enrichment_cache` with:

- IP
- country
- malicious flag
- reputation score
- raw payload
- update time
- expiry time

## Detector use

Built-in detectors consume enrichment fields in simple ways:

- malicious IPs can raise brute-force severity to `critical`
- suspicious web activity from flagged IPs is escalated
- anomaly alerts carry enrichment context in metadata

The goal is bounded context, not opaque scoring.
