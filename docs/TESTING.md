# TESTING

`0xchou00 — Lightweight Security Detection Tool`

## Preconditions

Service started locally:

```bash
sudo systemctl start 0xchou00.service
curl http://127.0.0.1:8000/health
```

Analyst key:

```bash
export ANALYST_KEY="siem-analyst-dev-key"
export VIEWER_KEY="siem-viewer-dev-key"
```

## SSH brute-force simulation

### Single request containing a burst

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${ANALYST_KEY}" \
  -d '{
    "source_type": "ssh",
    "lines": [
      "Apr 18 10:00:00 sensor sshd[1001]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
      "Apr 18 10:00:05 sensor sshd[1002]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
      "Apr 18 10:00:10 sensor sshd[1003]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
      "Apr 18 10:00:15 sensor sshd[1004]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2",
      "Apr 18 10:00:20 sensor sshd[1005]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2"
    ]
  }'
```

Expected:

- one `brute_force` alert
- `event_count >= 5`
- `source_ip == 203.0.113.50`

### Incremental burst using Bash

This path is closer to how the agent exercises rolling detector state:

```bash
for second in 00 05 10 15 20; do
  curl -s -X POST http://127.0.0.1:8000/ingest \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${ANALYST_KEY}" \
    -d "{
      \"source_type\": \"ssh\",
      \"lines\": [
        \"Apr 18 10:00:${second} sensor sshd[1001]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2\"
      ]
    }" > /dev/null
done
```

Retrieve alerts:

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=60" \
  -H "X-API-Key: ${VIEWER_KEY}"
```

## Web scanning simulation

### Sensitive path probes

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${ANALYST_KEY}" \
  -d '{
    "source_type": "nginx",
    "lines": [
      "203.0.113.50 - - [18/Apr/2026:10:01:00 +0000] \"GET /.env HTTP/1.1\" 404 123 \"-\" \"curl/8.0\"",
      "203.0.113.50 - - [18/Apr/2026:10:01:01 +0000] \"GET /admin HTTP/1.1\" 404 123 \"-\" \"curl/8.0\"",
      "203.0.113.50 - - [18/Apr/2026:10:01:02 +0000] \"GET /phpmyadmin HTTP/1.1\" 404 123 \"-\" \"curl/8.0\""
    ]
  }'
```

Expected:

- `suspicious_ip` alerts with `metadata.reason == "sensitive_path"`
- `yaml_rules` alerts for the scanning user agent
- if the SSH burst was already sent, one `correlation` alert joining SSH and web activity

### High-rate scan loop

This tests the request-rate detector rather than specific sensitive-path matches.

```bash
for i in $(seq 1 130); do
  curl -s -X POST http://127.0.0.1:8000/ingest \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${ANALYST_KEY}" \
    -d "{
      \"source_type\": \"nginx\",
      \"lines\": [
        \"198.51.100.77 - - [18/Apr/2026:10:02:${i} +0000] \\\"GET /healthcheck HTTP/1.1\\\" 404 12 \\\"-\\\" \\\"curl/8.0\\\"\"
      ]
    }" > /dev/null
done
```

Expected:

- one `suspicious_ip` alert with `metadata.reason == "request_rate"`

Note:
- This loop assumes the backend will accept synthetic timestamps from the log line itself.
- If your shell produces invalid second formatting after `59`, adjust the loop to generate a repeated minute or send a smaller windowed burst through a single request.

## Verification queries

Read alerts:

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=60" \
  -H "X-API-Key: ${VIEWER_KEY}"
```

Read enriched logs:

```bash
curl "http://127.0.0.1:8000/logs?since_minutes=60" \
  -H "X-API-Key: ${VIEWER_KEY}"
```

Verify integrity:

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: ${VIEWER_KEY}"
```

## Agent path test

If the agent is enabled on a Linux host, append directly to watched files:

```bash
echo 'Apr 18 10:05:00 sensor sshd[1009]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2' | sudo tee -a /var/log/auth.log
echo '203.0.113.50 - - [18/Apr/2026:10:05:01 +0000] "GET /.env HTTP/1.1" 404 123 "-" "curl/8.0"' | sudo tee -a /var/log/nginx/access.log
```

Watch agent logs:

```bash
journalctl -u 0xchou00-agent.service -f
```

Then query `/logs` and `/alerts` again to confirm the agent path reaches the same backend logic as manual ingestion.
