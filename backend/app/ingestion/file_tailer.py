from __future__ import annotations

import time
from pathlib import Path
from typing import Iterator


class FileTailer:
    """Yield log lines from a file in batch or tail mode."""

    def __init__(
        self,
        file_path: str | Path,
        *,
        poll_interval: float = 0.5,
        start_at_end: bool = False,
    ) -> None:
        self.file_path = Path(file_path)
        self.poll_interval = poll_interval
        self.start_at_end = start_at_end

    def read_existing(self) -> Iterator[str]:
        with self.file_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                cleaned = line.strip()
                if cleaned:
                    yield cleaned

    def follow(self) -> Iterator[str]:
        with self.file_path.open("r", encoding="utf-8", errors="replace") as handle:
            if self.start_at_end:
                handle.seek(0, 2)

            while True:
                line = handle.readline()
                if line:
                    cleaned = line.strip()
                    if cleaned:
                        yield cleaned
                    continue

                if not self.file_path.exists():
                    raise FileNotFoundError(f"Log file disappeared: {self.file_path}")

                time.sleep(self.poll_interval)
