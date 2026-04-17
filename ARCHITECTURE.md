# 0xchou00 platform architecture

## Clean architecture

The project is organized around one pipeline:

1. ingest raw telemetry
2. normalize it into a stable event schema
3. evaluate detections
4. persist logs and alerts
5. chain records for tamper evidence
6. expose everything through API and UI

This keeps the detection engine source-aware only where necessary and lets storage, integrity, and presentation remain separate concerns.

## File tree

```text
siem-project/
├── ARCHITECTURE.md
├── install.sh
├── README.md
├── TESTING.md
├── requirements.txt
├── backend/
│   ├── main.py
│   └── app/
│       ├── api/
│       │   ├── integrity.py
│       │   ├── routes.py
│       │   └── schemas.py
│       ├── core/
│       │   ├── config.py
│       │   └── pipeline.py
│       ├── detection/
│       │   ├── anomaly.py
│       │   ├── base.py
│       │   ├── brute_force.py
│       │   ├── engine.py
│       │   ├── suspicious_ip.py
│       │   └── yaml_rules.py
│       ├── ingestion/
│       │   ├── file_tailer.py
│       │   └── normalizer.py
│       ├── models/
│       │   ├── alert.py
│       │   └── event.py
│       ├── security/
│       │   └── rbac.py
│       ├── services/
│       │   ├── ingestion.py
│       │   ├── integrity.py
│       │   └── monitor.py
│       └── storage/
│           └── sqlite.py
├── deploy/
│   └── 0xchou00.service
├── frontend/
│   ├── brand-mark.svg
│   ├── dashboard.html
│   ├── dashboard.js
│   ├── landing.html
│   └── styles.css
├── logs/
├── media/
│   ├── 0xchou00_banner.svg
│   ├── linkedin_post.md
│   └── medium_article.md
├── rules/
│   └── default_rules.yml
└── scripts/
```

## Responsibility map

- `api`
  HTTP layer and request/response schemas.

- `core`
  Pipeline composition and runtime configuration.

- `detection`
  Detection logic only. Each detector stays isolated so behavior can change without touching ingestion or storage.

- `ingestion`
  Input handling and normalization so the rest of the system works on structured events instead of raw text.

- `models`
  Event and alert contracts shared across the platform.

- `security`
  Unified API-key RBAC enforcement.

- `services`
  Workflow orchestration that coordinates storage, integrity, and pipeline execution.

- `storage`
  SQLite persistence and integrity-chain state.
