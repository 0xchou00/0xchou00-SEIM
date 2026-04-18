# Security

## API keys

The tool uses API-key RBAC with three roles:

- `viewer`
- `analyst`
- `admin`

Default keys are seeded at startup for local testing. Replace them in `.env` before using the tool outside a disposable lab.

## Integrity

Every stored event and alert is appended to `chain_entries` with:

- payload hash
- previous entry hash
- entry hash
- creation time

`GET /integrity/verify` replays the chain and compares the stored payload hashes against the current database state.

This is tamper evidence, not distributed consensus.

## Enrichment safety

- GeoIP lookups are local when a database file is present
- AbuseIPDB is optional
- external threat-intelligence calls are cached and scheduled outside the main ingestion path

If enrichment fails, the tool continues with detector logic instead of dropping data.

## Agent trust boundary

The agent can read local log files and send them to the tool API. It should run on the host being observed or on a trusted collector node. Protect:

- `agent/config.yaml`
- `.env`
- the state file
- systemd unit files

## Limitations

- API keys are simple shared secrets, not a full identity system
- SQLite is suitable for one node, not hostile multi-writer deployments
- the dashboard stores the chosen API key in browser local storage for operator convenience
- the integrity chain detects tampering after the fact; it does not stop a privileged local attacker from deleting the database entirely
