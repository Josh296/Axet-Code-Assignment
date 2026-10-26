# Logscope Specification

## Purpose

Logscope is a command-line utility for incident responders to summarise application logs without using a dashboard.

## Supported input format

Each well-formed log line begins with a timestamp and log level followed by a message:

```text
2026-10-01 09:00:00 INFO Application started
2026-10-01T09:01:00Z ERROR Database connection refused
```

The parser must accept either a space-separated timestamp (`YYYY-MM-DD HH:MM:SS`) or ISO-8601 timestamp (`YYYY-MM-DDTHH:MM:SSZ`), followed by `INFO`, `WARN`, or `ERROR`, then the message. Other lines are malformed.

## Commands

### `logscope summary app.log`

Reports:

- Counts for `INFO`, `WARN`, and `ERROR`.
- Top five error messages, ordered by descending occurrence count and then message text.
- First and last valid timestamps.
- Count of malformed lines skipped.

### `logscope timeline app.log --bucket 15m`

Reports error counts grouped by a fixed bucket interval and renders a text bar chart. Supported bucket units are minutes (`m`) and hours (`h`). The report also includes malformed-line count.

### `logscope grep app.log --level ERROR --since "2026-10-01 09:00"`

Prints valid log lines matching the requested level and optional inclusive `--since` timestamp. It reports malformed-line count without treating malformed input as an error.

## Output formats

Every command accepts `--format json|md`.

- `json` writes structured data to standard output.
- `md` writes a Markdown report file in the current directory and prints its path. The default format is plain text for terminal use.

## Performance and reliability

- Process a 100 MB log as a stream without loading its full contents into memory.
- Malformed lines are counted and skipped; they must never crash the process.
- A synthetic 100 MB log generator must be available as `scripts/gen_log`.
- Processing the generated 100 MB log must finish in under 60 seconds with stable memory usage.

## Quality requirements

- Unit tests cover the parser and each command.
- Tests use `sample.log` to verify all three commands.
- Changes are made in small, reviewable stages following a reviewed plan.

## Stretch goal

`logscope explain` sends the top errors to an LLM endpoint configured by environment variables and prints a probable root-cause summary.
