# AGENT

`0xchou00 — Lightweight Security Detection Tool`

## Purpose

The agent is a file tailer and batch forwarder. It exists to move host-local log lines into the backend without embedding parsing or detection logic on the endpoint.

Implementation:
- `agent/agent.py`

Configuration:
- `agent/config.yaml`

## Watched sources

Each configured source defines:

- `source_type`
- `path`
- `start_at_end`

The default configuration watches:

- `/var/log/auth.log` as `ssh`
- `/var/log/nginx/access.log` as `nginx`

## Internal model

### Offset tracking

`OffsetTrackingTailer` tracks:

- current file inode
- current byte offset
- source type

State is persisted in JSON under `state_file`, typically `agent/state.json`.

This is what allows restart recovery:

- if the file inode is unchanged, the agent resumes from the saved offset
- if the inode changed, the agent assumes rotation and reopens the current path
- if no state exists and `start_at_end` is true, the first open seeks to the current file end

### Poll loop

The agent is polling-based.

For each configured source:

1. check file existence
2. reopen if inode changed or the handle is missing
3. read newly appended lines
4. strip trailing newlines
5. append non-empty lines to the in-memory buffer for that source type

No local parsing happens in the agent. Raw lines are forwarded unchanged.

## Buffering model

Buffers are held in memory per source type:

- `ssh`
- `nginx`
- any additional configured source types

Flush is triggered when either:

- buffered lines for any source reach `max_lines`
- elapsed time since the last flush reaches `flush_interval_seconds`

The agent sends one batch per source type. It does not mix SSH and web lines in the same request.

## Retry behavior

Requests are sent to `POST /ingest` with:

- JSON body containing `source_type` and `lines`
- `X-API-Key`

If the request fails for any reason:

- `_send_batch()` returns `False`
- that source buffer is not cleared
- the same buffered lines remain pending for the next flush cycle

This is deliberately simple:

- no spool directory
- no disk-backed retry queue
- no exponential backoff state

The tradeoff is bounded reliability. A long backend outage can grow in-memory buffers. The advantage is low operational complexity for a single-node deployment.

## Failure cases

### Backend unavailable

Effect:
- lines remain in memory
- the next flush cycle retries them

### File temporarily missing

Effect:
- the tailer closes the current handle
- polling continues
- when the path reappears, the tailer reopens and resumes from saved state if the inode matches

### Corrupt or missing state file

Effect:
- the agent starts with empty state
- source startup behavior falls back to each source's `start_at_end` setting

## Why the agent is separate

- Keeping the collector separate from the backend makes ingest path testing straightforward.
- The agent can be replaced or disabled without changing backend internals.
- The backend remains the only place where parsing, enrichment, detection, and correlation decisions are made.
