"""Streaming parser for supported application-log lines."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterator, TextIO


LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}(?:T| )\d{2}:\d{2}:\d{2}Z?)\s+"
    r"(?P<level>INFO|WARN|ERROR)\s+(?P<message>.*)$"
)


@dataclass(frozen=True)
class LogRecord:
    timestamp: datetime
    level: str
    message: str
    raw_line: str


def parse_line(line: str) -> LogRecord | None:
    """Parse one line, returning None when it does not match the log format."""
    raw_line = line.rstrip("\r\n")
    match = LINE_PATTERN.fullmatch(raw_line)
    if match is None:
        return None

    timestamp_text = match.group("timestamp")
    try:
        if "T" in timestamp_text:
            timestamp = datetime.strptime(timestamp_text, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
        else:
            timestamp = datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
    except ValueError:
        return None

    return LogRecord(
        timestamp=timestamp,
        level=match.group("level"),
        message=match.group("message"),
        raw_line=raw_line,
    )


def iter_records(stream: TextIO, malformed_count: list[int]) -> Iterator[LogRecord]:
    """Yield valid records from a stream and increment malformed_count for invalid lines."""
    for line in stream:
        record = parse_line(line)
        if record is None:
            malformed_count[0] += 1
            continue
        yield record
