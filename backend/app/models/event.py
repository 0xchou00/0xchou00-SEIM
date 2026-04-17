from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class LogEvent:
    timestamp: datetime
    source_type: str
    raw_message: str
    event_type: str
    source_ip: str | None = None
    hostname: str | None = None
    username: str | None = None
    process: str | None = None
    status: str | None = None
    severity: str = "info"
    http_method: str | None = None
    http_path: str | None = None
    http_status: int | None = None
    http_user_agent: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.astimezone(timezone.utc).isoformat()
        return data
