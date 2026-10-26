from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from logscope.analysis import build_timeline, parse_bucket, summarize
from logscope.parser import iter_records, parse_line


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_LOG = PROJECT_ROOT / "sample.log"


class ParserTests(unittest.TestCase):
    def test_parser_accepts_both_timestamp_formats(self) -> None:
        space_record = parse_line("2026-10-01 09:00:00 INFO Ready\n")
        iso_record = parse_line("2026-10-01T09:01:00Z ERROR Failed\n")

        self.assertEqual(space_record.timestamp, datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc))
        self.assertEqual(iso_record.timestamp, datetime(2026, 10, 1, 9, 1, tzinfo=timezone.utc))

    def test_parser_skips_and_counts_malformed_lines(self) -> None:
        malformed_count = [0]
        records = list(iter_records(io.StringIO("broken\n2026-10-01 09:00:00 INFO Good\n"), malformed_count))

        self.assertEqual(len(records), 1)
        self.assertEqual(malformed_count, [1])


class AnalysisTests(unittest.TestCase):
    def test_summary(self) -> None:
        result = summarize(SAMPLE_LOG)

        self.assertEqual(result.level_counts, {"INFO": 2, "WARN": 1, "ERROR": 3})
        self.assertEqual(result.top_errors[0], ("Database connection refused", 2))
        self.assertEqual(result.malformed_lines, 1)

    def test_timeline(self) -> None:
        items, malformed_lines = build_timeline(SAMPLE_LOG, parse_bucket("15m"))

        self.assertEqual([count for _, count in items], [1, 2])
        self.assertEqual(malformed_lines, 1)


class CommandTests(unittest.TestCase):
    def run_command(self, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "logscope", *arguments],
            cwd=cwd or PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_summary_json(self) -> None:
        output = self.run_command("summary", str(SAMPLE_LOG), "--format", "json")
        data = json.loads(output.stdout)

        self.assertEqual(data["level_counts"]["ERROR"], 3)
        self.assertEqual(data["malformed_lines"], 1)

    def test_timeline_text(self) -> None:
        output = self.run_command("timeline", str(SAMPLE_LOG), "--bucket", "15m")

        self.assertIn("Error timeline:", output.stdout)
        self.assertIn("#", output.stdout)
        self.assertIn("Malformed lines: 1", output.stdout)

    def test_grep_since(self) -> None:
        output = self.run_command(
            "grep", str(SAMPLE_LOG), "--level", "ERROR", "--since", "2026-10-01 09:15"
        )

        self.assertNotIn("09:10:00 ERROR", output.stdout)
        self.assertIn("09:15:00Z ERROR", output.stdout)
        self.assertIn("Malformed lines: 1", output.stdout)

    def test_markdown_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = self.run_command("summary", str(SAMPLE_LOG), "--format", "md", cwd=PROJECT_ROOT)
            report_path = Path(output.stdout.strip())
            try:
                self.assertTrue(report_path.exists())
                self.assertIn("# Logscope Summary", report_path.read_text(encoding="utf-8"))
            finally:
                report_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
