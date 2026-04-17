# 0xchou00 platform testing guide

This guide is written for a Linux user starting cold.

## 1. Install and start

```bash
cd siem-project
chmod +x install.sh
./install.sh
sudo systemctl start 0xchou00.service
sudo systemctl status 0xchou00.service
```

Confirm health:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok","logs":0,"alerts":0}
```

## 2. Use test API keys

- analyst: `siem-analyst-dev-key`
- viewer: `siem-viewer-dev-key`

## 3. Simulate SSH brute force

This scenario should trigger the brute-force detector and produce a visible alert in the dashboard.

```bash
for i in $(seq 1 6); do
  curl -X POST http://127.0.0.1:8000/ingest \
    -H "Content-Type: application/json" \
    -H "X-API-Key: siem-analyst-dev-key" \
    -d "{
      \"source_type\": \"ssh\",
      \"lines\": [
        \"Jan 15 03:21:0$i web01 sshd[$((1000+i))]: Failed password for root from 203.0.113.50 port $((55000+i)) ssh2\"
      ]
    }"
done
```

Expected alert behavior:

- detector: `brute_force`
- source IP: `203.0.113.50`
- severity: `high` or `critical`
- non-zero `event_count`

Verify:

```bash
curl "http://127.0.0.1:8000/alerts?since_minutes=60&source_type=ssh" \
  -H "X-API-Key: siem-viewer-dev-key"
```

## 4. Simulate suspicious web probing

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: siem-analyst-dev-key" \
  -d '{
    "source_type": "apache",
    "lines": [
      "198.51.100.10 - - [15/Jan/2024:03:02:00 +0000] \"GET /.env HTTP/1.1\" 404 209 \"-\" \"curl/8.0\""
    ]
  }'
```

Expected alert behavior:

- detector: `suspicious_ip`
- severity: `medium`
- metadata contains the probed path

## 5. Simulate YAML rule hit

This scenario targets the default invalid-user aggregation rule.

```bash
for i in $(seq 1 3); do
  curl -X POST http://127.0.0.1:8000/ingest \
    -H "Content-Type: application/json" \
    -H "X-API-Key: siem-analyst-dev-key" \
    -d "{
      \"source_type\": \"ssh\",
      \"lines\": [
        \"Jan 15 03:30:0$i web01 sshd[$((2000+i))]: Failed password for invalid user backup from 198.51.100.77 port $((56000+i)) ssh2\"
      ]
    }"
done
```

Expected alert behavior:

- detector: `yaml_rules`
- title: `Invalid SSH user burst`

## 6. Simulate anomaly spike

Warm the baseline first:

```bash
for round in $(seq 1 5); do
  for i in $(seq 1 3); do
    curl -X POST http://127.0.0.1:8000/ingest \
      -H "Content-Type: application/json" \
      -H "X-API-Key: siem-analyst-dev-key" \
      -d "{
        \"source_type\": \"apache\",
        \"lines\": [
          \"203.0.113.88 - - [15/Jan/2024:03:4$round:0$i +0000] \\\"GET / HTTP/1.1\\\" 200 1234 \\\"-\\\" \\\"Mozilla/5.0\\\"\"
        ]
      }"
  done
  sleep 61
done
```

Then spike the same source:

```bash
for i in $(seq 1 20); do
  curl -X POST http://127.0.0.1:8000/ingest \
    -H "Content-Type: application/json" \
    -H "X-API-Key: siem-analyst-dev-key" \
    -d "{
      \"source_type\": \"apache\",
      \"lines\": [
        \"203.0.113.88 - - [15/Jan/2024:03:59:$i +0000] \\\"GET /burst HTTP/1.1\\\" 200 1234 \\\"-\\\" \\\"Mozilla/5.0\\\"\"
      ]
    }"
done
```

Expected alert behavior:

- detector: `anomaly_frequency`
- description includes the current window count and baseline average

## 7. Verify integrity

```bash
curl http://127.0.0.1:8000/integrity/verify \
  -H "X-API-Key: siem-viewer-dev-key"
```

Expected:

- `valid: true`
- `entries` greater than zero
- `chain_head` populated

## 8. Verify the dashboard

1. Open `http://127.0.0.1:8000/`
2. Move to `/dashboard`
3. Enter `siem-viewer-dev-key`
4. Confirm:
   - alerts appear after ingest
   - logs appear after ingest
   - severity/source/time filters change results
   - connection state changes to `LIVE`

## 9. Troubleshooting

```bash
sudo systemctl status 0xchou00.service
journalctl -u 0xchou00.service -f
```

If alerts do not appear:

- check that the log format matches SSH or Apache/Nginx expectations
- check the selected time window in the dashboard
- check that the API key has enough privilege
