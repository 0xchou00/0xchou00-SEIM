from __future__ import annotations

from dataclasses import dataclass

from app.core.pipeline import ProcessingPipeline
from app.services.integrity import IntegrityService
from app.storage.sqlite import SQLiteStorage


@dataclass(slots=True)
class IngestionSummary:
    accepted: int
    parsed: int
    alerts: int
    alert_items: list[dict]


class IngestionService:
    """Persist normalized events and generated alerts from incoming log lines."""

    VALID_SOURCE_TYPES = {"ssh", "apache", "nginx", "web"}

    def __init__(
        self,
        pipeline: ProcessingPipeline | None = None,
        storage: SQLiteStorage | None = None,
        integrity: IntegrityService | None = None,
    ) -> None:
        self.pipeline = pipeline or ProcessingPipeline()
        self.storage = storage or SQLiteStorage()
        self.integrity = integrity or IntegrityService(self.storage)

    def ingest_lines(self, lines: list[str], source_type: str) -> IngestionSummary:
        normalized_source_type = source_type.strip().lower()
        if normalized_source_type not in self.VALID_SOURCE_TYPES:
            raise ValueError(
                f"Unsupported source_type '{source_type}'. "
                f"Expected one of: {sorted(self.VALID_SOURCE_TYPES)}"
            )

        accepted = 0
        parsed = 0
        alerts_created: list[dict] = []

        for raw_line in lines:
            if not isinstance(raw_line, str):
                continue
            line = raw_line.strip()
            if not line:
                continue

            accepted += 1
            result = self.pipeline.process_line(line, normalized_source_type)
            if result.event is None:
                continue

            parsed += 1
            event_id = self.storage.insert_event(result.event)
            self.integrity.record_log(event_id, result.event)

            for alert in result.alerts:
                self.storage.insert_alert(alert)
                self.integrity.record_alert(alert)
                alerts_created.append(alert.to_dict())

        return IngestionSummary(
            accepted=accepted,
            parsed=parsed,
            alerts=len(alerts_created),
            alert_items=alerts_created,
        )
