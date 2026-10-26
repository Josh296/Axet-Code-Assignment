# LogScope Specification

## Goal

Provide an incident-response command-line tool that summarizes application logs without requiring a dashboard.

## Log format

Each valid log entry starts with a timestamp, followed by a log level and message:

```text
2026-10-01 09:00:00 INFO Application started
2026-10-01T09:01:00Z ERROR Database connection failed
```

Supported levels are `INFO`, `WARN`, and `ERROR`. Lines that do not match this shape are malformed.

## Commands

### Summary

```text
logscope summary app.log
```

Reports:

- Counts for `INFO`, `WARN`, and `ERROR`
- The five most frequent error messages
- First and last valid timestamps
- Malformed-line count

### Timeline

```text
logscope timeline app.log --bucket 15m
```

Reports error counts per requested time bucket as a text bar chart, plus malformed-line count.

### Grep

```text
logscope grep app.log --level ERROR --since "2026-10-01 09:00"
```

Prints valid log lines matching the requested level and optional inclusive timestamp lower bound, plus malformed-line count.

## Output

Every command accepts:

```text
--format json|md
```

- `json` writes the command result to standard output as JSON.
- `md` writes a Markdown report file and reports its path.
- Default terminal output is readable text.

## Reliability and performance

- Stream the input file line by line; never load the complete file into memory.
- Process a 100 MB log in under 60 seconds with stable memory usage.
- Count and skip malformed lines; malformed input must never crash the CLI.

## Quality

- Unit-test the parser and every command.
- Include `scripts/gen_log` to generate a 100 MB synthetic log for benchmarking.
- Record benchmark runtime and memory measurements.

## Stretch goal

`logscope explain` sends top error messages to an LLM endpoint configured through environment variables and prints a probable root-cause summary.
