"""Command-line entry point for Logscope."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .analysis import build_timeline, grep_records, parse_bucket, summarize
from .render import format_output, grep_data, summary_data, timeline_data


def parse_since(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError as error:
        raise argparse.ArgumentTypeError("--since must use YYYY-MM-DD HH:MM") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logscope")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in ("summary", "timeline", "grep"):
        subparser = subcommands.add_parser(command)
        subparser.add_argument("log_file", type=Path)
        subparser.add_argument("--format", choices=("json", "md"), default="text")
        if command == "timeline":
            subparser.add_argument("--bucket", required=True)
        if command == "grep":
            subparser.add_argument("--level", choices=("INFO", "WARN", "ERROR"), required=True)
            subparser.add_argument("--since", type=parse_since)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    if args.command == "summary":
        data = summary_data(summarize(args.log_file))
    elif args.command == "timeline":
        try:
            interval = parse_bucket(args.bucket)
        except ValueError as error:
            raise SystemExit(f"logscope: {error}") from error
        items, malformed_lines = build_timeline(args.log_file, interval)
        data = timeline_data(items, malformed_lines)
    else:
        records, malformed_lines = grep_records(args.log_file, args.level, args.since)
        data = grep_data(records, malformed_lines)
    print(format_output(args.command, data, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
