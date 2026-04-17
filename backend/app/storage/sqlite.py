from __future__ import annotations

import json
import os
import secrets
import sqlite3
from hashlib import sha256
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.models.alert import Alert
from app.models.event import LogEvent


DEFAULT_DB_PATH = Path(
    os.getenv(
        "SIEM_DB_PATH",
        str(Path(__file__).resolve().parents[3] / "backend" / "data" / "0xchou00.db"),
    )
)


@dataclass(slots=True)
class APIKeyRecord:
    key_id: str
    name: str
    role: str
    is_active: bool


class SQLiteStorage:
    """SQLite-backed persistence for normalized logs, alerts, and API keys."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_ip TEXT,
                    hostname TEXT,
                    username TEXT,
                    severity TEXT NOT NULL,
                    raw_message TEXT NOT NULL,
                    normalized_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    detector TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_ip TEXT,
                    event_count INTEGER NOT NULL,
                    evidence_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    api_key TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chain_entries (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_logs_source_type ON logs(source_type, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_chain_sequence ON chain_entries(sequence);
                """
            )

        self.seed_default_api_keys()

    def seed_default_api_keys(self) -> None:
        defaults = {
            "admin": os.getenv("SIEM_ADMIN_API_KEY", "siem-admin-dev-key"),
            "analyst": os.getenv("SIEM_ANALYST_API_KEY", "siem-analyst-dev-key"),
            "viewer": os.getenv("SIEM_VIEWER_API_KEY", "siem-viewer-dev-key"),
        }

        with self.connection() as conn:
            for role, api_key in defaults.items():
                existing = conn.execute(
                    "SELECT id FROM api_keys WHERE api_key = ?",
                    (api_key,),
                ).fetchone()
                if existing:
                    continue

                conn.execute(
                    """
                    INSERT INTO api_keys (id, name, api_key, role, is_active, created_at)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (
                        secrets.token_urlsafe(12),
                        f"Default {role.title()} Key",
                        api_key,
                        role,
                        self._utc_now(),
                    ),
                )

    def validate_api_key(self, api_key: str) -> APIKeyRecord | None:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT id, name, role, is_active
                FROM api_keys
                WHERE api_key = ? AND is_active = 1
                """,
                (api_key,),
            ).fetchone()

        if not row:
            return None

        return APIKeyRecord(
            key_id=row["id"],
            name=row["name"],
            role=row["role"],
            is_active=bool(row["is_active"]),
        )

    def insert_event(self, event: LogEvent) -> int:
        payload = event.to_dict()
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO logs (
                    timestamp, source_type, event_type, source_ip, hostname,
                    username, severity, raw_message, normalized_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["timestamp"],
                    event.source_type,
                    event.event_type,
                    event.source_ip,
                    event.hostname,
                    event.username,
                    event.severity,
                    event.raw_message,
                    json.dumps(payload, sort_keys=True, default=str),
                    self._utc_now(),
                ),
            )
            return int(cursor.lastrowid)

    def insert_alert(self, alert: Alert) -> str:
        payload = alert.to_dict()
        with self.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO alerts (
                    id, detector, severity, title, description, source_type,
                    source_ip, event_count, evidence_json, metadata_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.alert_id,
                    alert.detector,
                    alert.severity,
                    alert.title,
                    alert.description,
                    alert.source_type,
                    alert.source_ip,
                    alert.event_count,
                    json.dumps(payload["evidence"]),
                    json.dumps(payload["metadata"]),
                    payload["created_at"],
                ),
            )
        return alert.alert_id

    def list_logs(
        self,
        *,
        limit: int = 100,
        source_type: str | None = None,
        event_type: str | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, timestamp, source_type, event_type, source_ip, hostname,
                   username, severity, raw_message, normalized_json, created_at
            FROM logs
        """
        conditions: list[str] = []
        params: list[Any] = []

        if source_type:
            conditions.append("source_type = ?")
            params.append(source_type)
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        if since:
            conditions.append("created_at >= ?")
            params.append(since)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["normalized"] = json.loads(item.pop("normalized_json"))
            results.append(item)
        return results

    def list_alerts(
        self,
        *,
        limit: int = 100,
        severity: str | None = None,
        detector: str | None = None,
        source_type: str | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, detector, severity, title, description, source_type,
                   source_ip, event_count, evidence_json, metadata_json, created_at
            FROM alerts
        """
        conditions: list[str] = []
        params: list[Any] = []

        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        if detector:
            conditions.append("detector = ?")
            params.append(detector)
        if source_type:
            conditions.append("source_type = ?")
            params.append(source_type)
        if since:
            conditions.append("created_at >= ?")
            params.append(since)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["evidence"] = json.loads(item.pop("evidence_json"))
            item["metadata"] = json.loads(item.pop("metadata_json"))
            results.append(item)
        return results

    def get_counts(self) -> dict[str, int]:
        with self.connection() as conn:
            logs_count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
            alerts_count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        return {"logs": int(logs_count), "alerts": int(alerts_count)}

    def append_chain_entry(self, entity_type: str, entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload_json = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = sha256(payload_json.encode("utf-8")).hexdigest()
        created_at = self._utc_now()

        with self.connection() as conn:
            previous = conn.execute(
                """
                SELECT sequence, entry_hash
                FROM chain_entries
                ORDER BY sequence DESC
                LIMIT 1
                """
            ).fetchone()
            prev_hash = previous["entry_hash"] if previous else "0" * 64
            entry_hash = self._compute_chain_hash(
                entity_type=entity_type,
                entity_id=entity_id,
                payload_hash=payload_hash,
                prev_hash=prev_hash,
                created_at=created_at,
            )
            cursor = conn.execute(
                """
                INSERT INTO chain_entries (
                    entity_type, entity_id, payload_hash, prev_hash, entry_hash, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (entity_type, entity_id, payload_hash, prev_hash, entry_hash, created_at),
            )
            sequence = int(cursor.lastrowid)

        return {
            "sequence": sequence,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
            "entry_hash": entry_hash,
            "created_at": created_at,
        }

    def verify_chain(self) -> dict[str, Any]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT sequence, entity_type, entity_id, payload_hash, prev_hash, entry_hash, created_at
                FROM chain_entries
                ORDER BY sequence ASC
                """
            ).fetchall()

        if not rows:
            return {
                "valid": True,
                "entries": 0,
                "chain_head": None,
                "errors": [],
            }

        expected_prev_hash = "0" * 64
        errors: list[str] = []

        for row in rows:
            item = dict(row)
            expected_hash = self._compute_chain_hash(
                entity_type=item["entity_type"],
                entity_id=item["entity_id"],
                payload_hash=item["payload_hash"],
                prev_hash=item["prev_hash"],
                created_at=item["created_at"],
            )

            if item["prev_hash"] != expected_prev_hash:
                errors.append(
                    f"Sequence {item['sequence']} has broken prev_hash linkage."
                )

            if item["entry_hash"] != expected_hash:
                errors.append(
                    f"Sequence {item['sequence']} has an invalid entry hash."
                )

            current_payload_hash = self._load_entity_payload_hash(
                entity_type=item["entity_type"],
                entity_id=item["entity_id"],
            )
            if current_payload_hash is None:
                errors.append(
                    f"Sequence {item['sequence']} references a missing {item['entity_type']} entity."
                )
            elif current_payload_hash != item["payload_hash"]:
                errors.append(
                    f"Sequence {item['sequence']} payload hash does not match the stored {item['entity_type']} entity."
                )

            expected_prev_hash = item["entry_hash"]

        return {
            "valid": len(errors) == 0,
            "entries": len(rows),
            "chain_head": rows[-1]["entry_hash"],
            "errors": errors,
        }

    def _compute_chain_hash(
        self,
        *,
        entity_type: str,
        entity_id: str,
        payload_hash: str,
        prev_hash: str,
        created_at: str,
    ) -> str:
        material = json.dumps(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "payload_hash": payload_hash,
                "prev_hash": prev_hash,
                "created_at": created_at,
            },
            sort_keys=True,
        )
        return sha256(material.encode("utf-8")).hexdigest()

    def _load_entity_payload_hash(self, *, entity_type: str, entity_id: str) -> str | None:
        with self.connection() as conn:
            if entity_type == "log":
                row = conn.execute(
                    "SELECT normalized_json FROM logs WHERE id = ?",
                    (entity_id,),
                ).fetchone()
                if not row:
                    return None
                payload = row["normalized_json"]
            elif entity_type == "alert":
                row = conn.execute(
                    """
                    SELECT id, detector, severity, title, description, source_type, source_ip,
                           event_count, evidence_json, metadata_json, created_at
                    FROM alerts
                    WHERE id = ?
                    """,
                    (entity_id,),
                ).fetchone()
                if not row:
                    return None
                payload = json.dumps(
                    {
                        "alert_id": row["id"],
                        "detector": row["detector"],
                        "severity": row["severity"],
                        "title": row["title"],
                        "description": row["description"],
                        "source_type": row["source_type"],
                        "source_ip": row["source_ip"],
                        "event_count": row["event_count"],
                        "evidence": json.loads(row["evidence_json"]),
                        "metadata": json.loads(row["metadata_json"]),
                        "created_at": row["created_at"],
                    },
                    sort_keys=True,
                )
            else:
                return None

        return sha256(payload.encode("utf-8")).hexdigest()

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
