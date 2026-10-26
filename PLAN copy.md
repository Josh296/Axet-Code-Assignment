# Logscope Implementation Plan

## Scope and design choices

- Language: Python 3 standard library.
- Package layout: `logscope/` for reusable logic, `tests/` for `unittest` coverage, and `scripts/` for operational helpers.
- Input is read line-by-line. Aggregations retain only bounded state: counters, five-or-more distinct error message counts, and timeline bucket counts.
- Markdown reports are written to a deterministic, command-specific file beside the current working directory.

## Build stages

1. **Parser**
   - Define a log-record model and a parser accepting the two timestamp formats in `SPEC.md`.
   - Provide a streaming iterator that returns valid records while incrementing malformed-line count.
   - Add parser unit tests for both formats and invalid input.

2. **Summary**
   - Build streaming level counts, first/last timestamp, and error-message frequency aggregation.
   - Add a `summary` subcommand and plain-text renderer.
   - Add command tests against `sample.log`.

3. **Timeline**
   - Parse `--bucket` values for minute/hour durations.
   - Aggregate only `ERROR` records into aligned time buckets and render scaled text bars.
   - Add timeline unit and command tests.

4. **Grep**
   - Support required `--level` and optional inclusive `--since` filter.
   - Stream matching original lines to the renderer and report malformed input.
   - Add grep unit and command tests.

5. **Output formats**
   - Add shared JSON and Markdown serializers for all commands.
   - Write Markdown reports to files and test their content/path behavior.

6. **Operational validation**
   - Add executable `scripts/gen_log` to write synthetic log data incrementally to an exact requested size.
   - Generate a 100 MB file, measure elapsed runtime and peak memory, and document the result in `BENCHMARK.md`.

## Verification

- Run focused `python -m unittest` tests after each stage.
- Run the full test suite and the three commands against `sample.log` at the end.
- Run the 100 MB summary benchmark and confirm completion below 60 seconds with bounded memory.

## Explicit exclusions

- The `explain` LLM integration is deferred until the core acceptance criteria are complete and separately approved.
