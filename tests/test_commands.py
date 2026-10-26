import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from logscope.analysis import build_timeline, parse_bucket, summarize


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_LOG = PROJECT_ROOT / "sample.log"


class AnalysisTests(unittest.TestCase):
    def test_summary_counts_levels_errors_timestamps_and_malformed_lines(self) -> None:
        result = summarize(SAMPLE_LOG)

        self.assertEqual(result.level_counts, {"INFO": 2, "WARN": 1, "ERROR": 3})
        self.assertEqual(
            result.top_errors,
            [("Database connection refused", 2), ("Request timed out", 1)],
        )
        self.assertEqual(result.malformed_lines, 1)
        self.assertEqual(str(result.first_timestamp), "2026-10-01 09:00:00")
        self.assertEqual(str(result.last_timestamp), "2026-10-01 09:25:00")

    def test_timeline_groups_errors(self) -> None:
        items, malformed_lines = build_timeline(SAMPLE_LOG, parse_bucket("15m"))

        self.assertEqual([count for _, count in items], [1, 2])
        self.assertEqual(malformed_lines, 1)

    def test_invalid_bucket_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_bucket("0m")
        with self.assertRaises(ValueError):
            parse_bucket("15d")


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
        result = self.run_command("summary", str(SAMPLE_LOG), "--format", "json")
        data = json.loads(result.stdout)

        self.assertEqual(data["level_counts"]["ERROR"], 3)
        self.assertEqual(data["malformed_lines"], 1)

    def test_timeline_text(self) -> None:
        result = self.run_command("timeline", str(SAMPLE_LOG), "--bucket", "15m")

        self.assertIn("Error timeline:", result.stdout)
        self.assertIn("Malformed lines: 1", result.stdout)
        self.assertIn("#", result.stdout)

    def test_grep_since_filters_records(self) -> None:
        result = self.run_command(
            "grep",
            str(SAMPLE_LOG),
            "--level",
            "ERROR",
            "--since",
            "2026-10-01 09:15",
        )

        self.assertNotIn("2026-10-01 09:10:00 ERROR", result.stdout)
        self.assertIn("2026-10-01T09:15:00Z ERROR", result.stdout)
        self.assertIn("Malformed lines: 1", result.stdout)

    def test_markdown_writes_report_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            result = self.run_command(
                "summary", str(SAMPLE_LOG), "--format", "md", cwd=temporary_path
            )
            report_path = Path(result.stdout.strip())

            self.assertEqual(report_path, temporary_path / "logscope-summary-report.md")
            self.assertIn("# Logscope Summary", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
