# 0xchou00 Detection Tool Testing Guide

## 1. Install and start

```bash
cd siem-project
chmod +x install.sh
./install.sh
sudo systemctl start 0xchou00.service
sudo systemctl start 0xchou00-agent.service
```

Check status:

```bash
sudo systemctl status 0xchou00.service
sudo systemctl status 0xchou00-agent.service
curl http://127.0.0.1:8000/health
```

## 2. Test API keys

- analyst: `siem-analyst-dev-key`
- viewer: `siem-viewer-dev-key`

## 3. SSH brute force

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

Expected:

- at least one `brute_force` alert
- `event_count >= 5`
- source IP `203.0.113.50`

## 4. Sensitive web probing

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: siem-analyst-dev-key" \
  -d '{
    "source_type": "nginx",
    "lines": [
      "203.0.113.50 - - [15/Jan/2026:03:22:00 +0000] \"GET /.env HTTP/1.1\" 404 123 \"-\" \"curl/8.0\"",
      "203.0.113.50 - - [15/Jan/2026:03:22:01 +0000] \"GET /.git/config HTTP/1.1\" 404 123 \"-\" \"curl/8.0\""
    ]
  }'
```

Expected:

- `suspicious_ip` alerts for sensitive paths
- `yaml_rules` alerts for scanner user agents
- one `correlation` alert tying SSH and web behavior together

## 5. Enrichment verification

Read logs:

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Expected fields on each event:

- `country`
- `is_malicious`
- `reputation_score`
- `enrichment_source`

If `203.0.113.50` remains in `rules/static_blacklist.txt`, the event should show:

- `is_malicious: true`
- `enrichment_source: static_blacklist`

## 6. Correlation verification

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=60" \
  -H "X-API-Key: siem-viewer-dev-key"
```

Expected correlation fields:

- `detector: correlation`
- `alert_kind: correlation`
- `correlation_rule_id`
- evidence containing the matched detector alerts

## 7. Agent verification

Update `agent/config.yaml` if needed, then:

```bash
sudo systemctl restart 0xchou00-agent.service
journalctl -u 0xchou00-agent.service -f
```

Append a line to a watched log file and confirm:

- the line is forwarded to `/ingest`
- `/logs` count increases
- `agent/state.json` updates with the latest offset

## 8. Integrity verification

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: siem-viewer-dev-key"
```

Expected:

- `valid: true`
- `entries > 0`
- `chain_head` populated

## 9. Dashboard verification

1. Open `http://127.0.0.1:8000/dashboard`
2. Enter `siem-viewer-dev-key`
3. Confirm:
   - logs show enrichment fields
   - alerts show detector and correlation output
   - severity and source filters change the result set

## 10. Troubleshooting

```bash
sudo systemctl status 0xchou00.service
sudo systemctl status 0xchou00-agent.service
journalctl -u 0xchou00.service -f
journalctl -u 0xchou00-agent.service -f
```
