# LogScope Implementation Plan

## Constraints and decisions

- Language: Python 3 with the standard library.
- Package layout: `src/logscope/` with an executable module invoked as `python -m logscope` during development.
- Valid entries: `YYYY-MM-DD[ T]HH:MM[:SS][Z|±HH:MM] LEVEL message`; naive timestamps are interpreted consistently as local-naive values.
- Input is processed as a stream. Aggregations retain only counters, timestamps, up to five error-message candidates, and timeline buckets.
- Markdown output is written beside the input log as a command-specific `*.report.md` file unless a later interface decision adds an output-path option.

## Implementation stages

1. **Parser foundation**
   - Add project packaging and a parser yielding structured records.
   - Normalize supported timestamps and preserve original matching lines.
   - Count malformed lines without raising.
   - Add parser unit tests for valid formats, invalid lines, and timestamps.
   - Run parser tests.

2. **Summary command**
   - Add CLI argument parsing and `summary` aggregation.
   - Calculate level counts, top five error messages, first/last timestamps, and malformed count.
   - Add summary unit and CLI tests.
   - Run the focused and full test suites.

3. **Timeline command**
   - Parse minute/hour bucket durations such as `15m`.
   - Aggregate `ERROR` records into aligned buckets and render text bars.
   - Add timeline unit and CLI tests.
   - Run tests.

4. **Grep command**
   - Filter streamed records by required level and optional inclusive `--since` timestamp.
   - Emit selected original lines while reporting malformed count.
   - Add grep unit and CLI tests.
   - Run tests.

5. **Output formats**
   - Add `--format json|md` to each command while retaining readable terminal output by default.
   - Serialize a stable machine-readable result and generate Markdown reports.
   - Add output-format tests for every command.
   - Run the full test suite.

6. **Sample data and benchmark tooling**
   - Add `sample.log` covering valid entries, repeated errors, and malformed lines.
   - Add executable `scripts/gen_log` which streams deterministic synthetic entries until its requested size (default: 100 MB).
   - Add a benchmark runner using `time.perf_counter()` and `tracemalloc` or platform resource metrics; document the result.
   - Generate and process a 100 MB file, verifying runtime below 60 seconds and stable memory.

## Validation

- `python -m unittest discover -s tests -v` after each stage.
- Smoke-test all three commands against `sample.log` in text, JSON, and Markdown modes.
- Benchmark only after functional tests pass.

## Version-control note

The environment does not have a `git` executable available, so Git initialization and commit history cannot be created here. Per the request, implementation stages will instead be manually updated only after explicit permission.
