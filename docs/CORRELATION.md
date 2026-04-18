# Correlation

## Purpose

Correlation runs after detector alerts are created. It looks for short attack sequences that are more meaningful together than alone.

Examples:

- SSH brute force followed by suspicious web probing from the same IP
- traffic spike plus sensitive path access

## Rules file

Correlation rules live in:

- `rules/correlation_rules.yml`

Example structure:

```yaml
rules:
  - id: ssh_bruteforce_then_web_scan
    title: SSH brute force followed by web scanning
    description: The same source triggered SSH brute-force activity and suspicious web behavior inside a five-minute window.
    severity: critical
    conditions:
      time_window_seconds: 300
      same_source_ip: true
      alerts:
        - detector: brute_force
        - detector: suspicious_ip
```

## Matching logic

For each new detector alert:

1. load correlation rules
2. select rules that mention the current detector
3. query recent detector alerts from SQLite
4. check rule selectors against those stored alerts
5. emit one correlation alert per rule, source IP, and correlation window

## Stored output

Correlation alerts are stored in the same `alerts` table as detector alerts with:

- `detector = correlation`
- `alert_kind = correlation`
- `correlation_rule_id`
- `correlation_fingerprint`

Because they are ordinary alerts, they are already visible through:

- `GET /alerts`
- the bundled operator UI

## Why this shape

This approach keeps the tool small:

- no separate stream processor
- no rule engine outside the codebase
- no extra alert store

The tradeoff is that correlation remains intentionally simple and time-window based.
