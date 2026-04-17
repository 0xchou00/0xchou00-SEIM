from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import PipelineConfig
from app.detection.engine import DetectionEngine
from app.ingestion.normalizer import LogNormalizer
from app.models.alert import Alert
from app.models.event import LogEvent


@dataclass(slots=True)
class PipelineResult:
    event: LogEvent | None
    alerts: list[Alert] = field(default_factory=list)


class ProcessingPipeline:
    """Coordinate normalization and detection for incoming log lines."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.normalizer = LogNormalizer()
        self.engine = DetectionEngine(self.config)

    def process_line(self, raw_line: str, source_type: str) -> PipelineResult:
        event = self.normalizer.normalize(raw_line=raw_line, source_type=source_type)
        if event is None:
            return PipelineResult(event=None, alerts=[])

        alerts = self.engine.process(event)
        return PipelineResult(event=event, alerts=alerts)
