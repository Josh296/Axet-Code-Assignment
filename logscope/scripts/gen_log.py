"""Generate a deterministic synthetic application log without retaining it in memory."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path


TEMPLATES = (
    "INFO Application started",
    "INFO Request completed",
    "WARN Cache miss",
    "ERROR Database connection refused",
    "ERROR Request timed out",
)


def build_line(index: int) -> bytes:
    timestamp = datetime(2026, 10, 1, 9, 0, 0) + timedelta(seconds=index)
    return f"{timestamp:%Y-%m-%d %H:%M:%S} {TEMPLATES[index % len(TEMPLATES)]}\n".encode(
        "utf-8"
    )


def generate(output_path: Path, size_bytes: int) -> None:
    written = 0
    index = 0
    with output_path.open("wb") as stream:
        while written < size_bytes:
            line = build_line(index)
            remaining = size_bytes - written
            stream.write(line[:remaining])
            written += min(len(line), remaining)
            index += 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a synthetic Logscope input file.")
    parser.add_argument("output", type=Path)
    parser.add_argument("--size-mb", type=int, default=100)
    args = parser.parse_args()
    if args.size_mb <= 0:
        parser.error("--size-mb must be greater than zero")
    generate(args.output, args.size_mb * 1024 * 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
