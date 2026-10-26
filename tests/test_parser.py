from datetime import datetime, timezone
import io
import unittest

from logscope.parser import iter_records, parse_line


class ParseLineTests(unittest.TestCase):
    def test_parses_space_separated_timestamp(self) -> None:
        record = parse_line("2026-10-01 09:00:00 INFO Application started\n")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.timestamp, datetime(2026, 10, 1, 9, 0, 0))
        self.assertEqual(record.level, "INFO")
        self.assertEqual(record.message, "Application started")

    def test_parses_iso_timestamp(self) -> None:
        record = parse_line("2026-10-01T09:15:00Z ERROR Database unavailable\n")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.timestamp, datetime(2026, 10, 1, 9, 15, tzinfo=timezone.utc))
        self.assertEqual(record.level, "ERROR")

    def test_rejects_malformed_lines(self) -> None:
        self.assertIsNone(parse_line("not a valid line\n"))
        self.assertIsNone(parse_line("2026-10-01 09:00:00 DEBUG Unknown level\n"))
        self.assertIsNone(parse_line("2026-99-01 09:00:00 INFO Invalid date\n"))


class IterRecordsTests(unittest.TestCase):
    def test_yields_valid_records_and_counts_malformed_lines(self) -> None:
        stream = io.StringIO(
            "2026-10-01 09:00:00 INFO Valid\n"
            "broken\n"
            "2026-10-01T09:01:00Z ERROR Also valid\n"
        )
        malformed_count = [0]

        records = list(iter_records(stream, malformed_count))

        self.assertEqual([record.level for record in records], ["INFO", "ERROR"])
        self.assertEqual(malformed_count, [1])


if __name__ == "__main__":
    unittest.main()
