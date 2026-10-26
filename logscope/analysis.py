"""Streaming aggregations for Logscope commands."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .parser import LogRecord, iter_records


@dataclass(frozen=True)
class SummaryResult:
    level_counts: dict[str, int]
    top_errors: list[tuple[str, int]]
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    malformed_lines: int


def summarize(log_path: Path) -> SummaryResult:
    level_counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
    error_counts: Counter[str] = Counter()
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    malformed_count = [0]
    with log_path.open("r", encoding="utf-8", errors="replace") as stream:
        for record in iter_records(stream, malformed_count):
            level_counts[record.level] += 1
            if record.level == "ERROR":
                error_counts[record.message] += 1
            if first_timestamp is None or record.timestamp < first_timestamp:
                first_timestamp = record.timestamp
            if last_timestamp is None or record.timestamp > last_timestamp:
                last_timestamp = record.timestamp
    return SummaryResult(
        level_counts,
        sorted(error_counts.items(), key=lambda item: (-item[1], item[0]))[:5],
        first_timestamp,
        last_timestamp,
        malformed_count[0],
    )


def parse_bucket(bucket: str) -> timedelta:
    if len(bucket) < 2 or bucket[-1] not in {"m", "h"}:
        raise ValueError("bucket must be a positive integer followed by m or h")
    try:
        value = int(bucket[:-1])
    except ValueError as error:
        raise ValueError("bucket must be a positive integer followed by m or h") from error
    if value <= 0:
        raise ValueError("bucket must be greater than zero")
    return timedelta(minutes=value) if bucket[-1] == "m" else timedelta(hours=value)


def bucket_start(timestamp: datetime, interval: timedelta) -> datetime:
    epoch = datetime(1970, 1, 1, tzinfo=timestamp.tzinfo)
    interval_seconds = int(interval.total_seconds())
    elapsed_seconds = int((timestamp - epoch).total_seconds())
    return epoch + timedelta(seconds=elapsed_seconds // interval_seconds * interval_seconds)


def build_timeline(log_path: Path, interval: timedelta) -> tuple[list[tuple[datetime, int]], int]:
    counts: Counter[datetime] = Counter()
    malformed_count = [0]
    with log_path.open("r", encoding="utf-8", errors="replace") as stream:
        for record in iter_records(stream, malformed_count):
            if record.level == "ERROR":
                counts[bucket_start(record.timestamp, interval)] += 1
    return sorted(counts.items()), malformed_count[0]


def grep_records(log_path: Path, level: str, since: datetime | None) -> tuple[list[LogRecord], int]:
    matches: list[LogRecord] = []
    malformed_count = [0]
    with log_path.open("r", encoding="utf-8", errors="replace") as stream:
        for record in iter_records(stream, malformed_count):
            if record.level == level and (since is None or record.timestamp >= since):
                matches.append(record)
    return matches, malformed_count[0]
