from __future__ import annotations

from app.models.alert import Alert
from app.models.event import LogEvent
from app.storage.sqlite import SQLiteStorage


class IntegrityService:
    """Hash-chain persistence and verification for logs and alerts."""

    def __init__(self, storage: SQLiteStorage | None = None) -> None:
        self.storage = storage or SQLiteStorage()

    def record_log(self, event_id: int, event: LogEvent) -> dict:
        return self.storage.append_chain_entry(
            entity_type="log",
            entity_id=str(event_id),
            payload=event.to_dict(),
        )

    def record_alert(self, alert: Alert) -> dict:
        return self.storage.append_chain_entry(
            entity_type="alert",
            entity_id=alert.alert_id,
            payload=alert.to_dict(),
        )

    def verify(self) -> dict:
        return self.storage.verify_chain()
