from __future__ import annotations

from collections.abc import Callable, Iterator

from app.core.pipeline import ProcessingPipeline, PipelineResult
from app.ingestion.file_tailer import FileTailer


class LogMonitorService:
    """High-level service for file-based real-time processing."""

    def __init__(self, pipeline: ProcessingPipeline | None = None) -> None:
        self.pipeline = pipeline or ProcessingPipeline()

    def stream_file(
        self,
        file_path: str,
        source_type: str,
        *,
        start_at_end: bool = False,
    ) -> Iterator[PipelineResult]:
        tailer = FileTailer(file_path, start_at_end=start_at_end)
        for line in tailer.follow():
            yield self.pipeline.process_line(line, source_type)

    def process_existing_file(self, file_path: str, source_type: str) -> list[PipelineResult]:
        tailer = FileTailer(file_path)
        return [self.pipeline.process_line(line, source_type) for line in tailer.read_existing()]

    def watch_file(
        self,
        file_path: str,
        source_type: str,
        on_result: Callable[[PipelineResult], None],
        *,
        start_at_end: bool = False,
    ) -> None:
        for result in self.stream_file(file_path, source_type, start_at_end=start_at_end):
            on_result(result)
