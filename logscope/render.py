"""Plain text, JSON, and Markdown output for Logscope."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from .analysis import SummaryResult
from .parser import LogRecord


def timestamp_text(timestamp: datetime | None) -> str | None:
    return timestamp.isoformat(sep=" ") if timestamp is not None else None


def summary_data(result: SummaryResult) -> dict[str, Any]:
    return {
        "level_counts": result.level_counts,
        "top_errors": [
            {"message": message, "count": count} for message, count in result.top_errors
        ],
        "first_timestamp": timestamp_text(result.first_timestamp),
        "last_timestamp": timestamp_text(result.last_timestamp),
        "malformed_lines": result.malformed_lines,
    }


def timeline_data(items: list[tuple[datetime, int]], malformed_lines: int) -> dict[str, Any]:
    return {
        "buckets": [
            {"timestamp": timestamp_text(timestamp), "error_count": count}
            for timestamp, count in items
        ],
        "malformed_lines": malformed_lines,
    }


def grep_data(records: list[LogRecord], malformed_lines: int) -> dict[str, Any]:
    return {
        "lines": [record.raw_line for record in records],
        "malformed_lines": malformed_lines,
    }


def render_summary_text(data: dict[str, Any]) -> str:
    lines = ["Level counts:"]
    lines.extend(f"  {level}: {data['level_counts'][level]}" for level in ("INFO", "WARN", "ERROR"))
    lines.append("Top errors:")
    lines.extend(
        f"  {item['count']} {item['message']}" for item in data["top_errors"]
    )
    if not data["top_errors"]:
        lines.append("  None")
    lines.extend(
        [
            f"First timestamp: {data['first_timestamp'] or 'None'}",
            f"Last timestamp: {data['last_timestamp'] or 'None'}",
            f"Malformed lines: {data['malformed_lines']}",
        ]
    )
    return "\n".join(lines)


def render_timeline_text(data: dict[str, Any]) -> str:
    buckets = data["buckets"]
    largest = max((item["error_count"] for item in buckets), default=0)
    lines = ["Error timeline:"]
    for item in buckets:
        width = max(1, round(item["error_count"] * 40 / largest)) if largest else 0
        lines.append(f"{item['timestamp']} | {'#' * width} {item['error_count']}")
    if not buckets:
        lines.append("No errors")
    lines.append(f"Malformed lines: {data['malformed_lines']}")
    return "\n".join(lines)


def render_grep_text(data: dict[str, Any]) -> str:
    lines = list(data["lines"])
    lines.append(f"Malformed lines: {data['malformed_lines']}")
    return "\n".join(lines)


def render_markdown(command: str, data: dict[str, Any]) -> str:
    if command == "summary":
        lines = ["# Logscope Summary", "", "## Level counts", ""]
        lines.extend(f"- **{level}**: {data['level_counts'][level]}" for level in ("INFO", "WARN", "ERROR"))
        lines.extend(["", "## Top errors", ""])
        lines.extend(f"- {item['count']} — {item['message']}" for item in data["top_errors"])
        if not data["top_errors"]:
            lines.append("- None")
        lines.extend(["", f"- First timestamp: {data['first_timestamp'] or 'None'}", f"- Last timestamp: {data['last_timestamp'] or 'None'}"])
    elif command == "timeline":
        lines = ["# Logscope Error Timeline", "", "| Bucket | Errors |", "| --- | ---: |"]
        lines.extend(f"| {item['timestamp']} | {item['error_count']} |" for item in data["buckets"])
    else:
        lines = ["# Logscope Filtered Lines", ""]
        lines.extend(f"- `{line}`" for line in data["lines"])
    lines.extend(["", f"Malformed lines: {data['malformed_lines']}"])
    return "\n".join(lines) + "\n"


def write_markdown_report(command: str, markdown: str) -> Path:
    report_path = Path.cwd() / f"logscope-{command}-report.md"
    report_path.write_text(markdown, encoding="utf-8")
    return report_path


def format_output(command: str, data: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format == "md":
        return str(write_markdown_report(command, render_markdown(command, data)))
    if command == "summary":
        return render_summary_text(data)
    if command == "timeline":
        return render_timeline_text(data)
    return render_grep_text(data)
