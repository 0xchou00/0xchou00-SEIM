# Agent

## Purpose

The agent tails local log files and forwards new lines to `POST /ingest` in batches. It exists to make the tool useful on a Linux host without requiring manual curl requests for every test.

## Files

- `agent/agent.py`
- `agent/config.yaml`
- `deploy/0xchou00-agent.service`

## Default sources

- `/var/log/auth.log` as `ssh`
- `/var/log/nginx/access.log` as `nginx`

## Behavior

- follows files in a `tail -F` style loop
- tracks byte offsets and inode state in `agent/state.json`
- survives restarts without replaying the whole file
- detects file rotation by inode change and reopens the path
- flushes batches when either:
  - `max_lines` is reached
  - `flush_interval_seconds` expires

## Configuration

`agent/config.yaml`

```yaml
api:
  url: "http://127.0.0.1:8000/ingest"
  api_key: "siem-analyst-dev-key"
batch:
  max_lines: 25
  flush_interval_seconds: 3
tail:
  poll_interval_seconds: 0.5
state_file: "./agent/state.json"
sources:
  - source_type: "ssh"
    path: "/var/log/auth.log"
    start_at_end: true
```

## Run manually

```bash
python3 agent/agent.py --config agent/config.yaml
```

## systemd

Install script integration enables:

- `0xchou00.service`
- `0xchou00-agent.service`

Start the agent:

```bash
sudo systemctl start 0xchou00-agent.service
sudo systemctl status 0xchou00-agent.service
```

## Failure behavior

- if the API is unavailable, the agent keeps buffered lines in memory and retries on the next flush cycle
- if a tailed file disappears temporarily, the agent waits for it to return and resumes from the tracked path state
- if the state file is missing, the agent starts from the end of each configured log when `start_at_end: true`
