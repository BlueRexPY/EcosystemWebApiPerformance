"""Markdown and console output formatters for benchmark results."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import ECOSYSTEMS, SCENARIOS, Ecosystem, Scenario, result_path
from .metrics import BenchmarkResult


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_result_md(result: BenchmarkResult) -> Path:
    """Write a single benchmark result as a Markdown file."""
    eco = ECOSYSTEMS.get(result.ecosystem)
    if eco is None:
        raise ValueError(f"Unknown ecosystem: {result.ecosystem}")

    path = result_path(
        eco,
        SCENARIOS.get(
            result.scenario, Scenario(result.scenario, "GET", "/", result.scenario)
        ),
        result.client,
    )
    _ensure_dir(path)

    status_breakdown = (
        "\n".join(
            f"| {code} | {count:,} |"
            for code, count in sorted(result.status_codes.items())
        )
        if result.status_codes
        else "| — | — |"
    )

    error_note = ""
    if result.error_count > 0:
        error_note = (
            f"\n> **Warning**: {result.error_count} errors occurred during this test.\n"
        )

    content = f"""# {eco.display_name} — {result.scenario} Benchmark

**Tested**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
**Client**: {result.client}
**Duration**: {result.duration_seconds:.1f}s
{error_note}
## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | {result.total_requests:,} |
| Requests/sec | {result.requests_per_sec:,.2f} |
| Duration | {result.duration_seconds:.2f}s |
| Errors | {result.error_count} |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | {result.min_ms:.2f}ms |
| avg | {result.avg_ms:.2f}ms |
| stdev | {result.stdev_ms:.2f}ms |
| p50 | {result.p50_ms:.2f}ms |
| p75 | {result.p75_ms:.2f}ms |
| p90 | {result.p90_ms:.2f}ms |
| p95 | {result.p95_ms:.2f}ms |
| p99 | {result.p99_ms:.2f}ms |
| p99.9 | {result.p999_ms:.2f}ms |
| max | {result.max_ms:.2f}ms |

## Status Codes

| Code | Count |
| --- | --- |
{status_breakdown}

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | {result.memory.mem_usage} |
| Memory Limit | {result.memory.mem_limit} |
| Memory % | {result.memory.mem_percent} |
| CPU % | {result.memory.cpu_percent} |
| PIDs | {result.memory.pids} |

## Raw Output

```
{result.raw_output.strip()}
```
"""
    path.write_text(content, encoding="utf-8")
    return path


def write_summary_md(
    results: list[BenchmarkResult], title: str = "Load Test Summary"
) -> Path:
    """Generate a combined summary markdown for multiple results."""
    from .config import RESULTS_DIR

    _ensure_dir(RESULTS_DIR / ".keep")

    rows: list[str] = []
    for r in results:
        eco_name = ECOSYSTEMS.get(
            r.ecosystem, Ecosystem(r.ecosystem, r.ecosystem, 0, "")
        ).display_name
        mem = r.memory.mem_usage or "N/A"
        rps = f"{r.requests_per_sec:,.2f}" if r.success else "FAILED"
        rows.append(
            f"| {eco_name} | {r.scenario} | {r.client} | {rps} | "
            f"{r.avg_ms:.2f}ms | {r.p50_ms:.2f}ms | {r.p95_ms:.2f}ms | "
            f"{r.p99_ms:.2f}ms | {r.p999_ms:.2f}ms | {r.max_ms:.2f}ms | "
            f"{r.total_requests:,} | {r.error_count} | {mem} |"
        )

    table_rows = "\n".join(rows)

    content = f"""# {title}

**Generated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}

## Results

| Ecosystem | Scenario | Client | Req/sec | Avg | p50 | p95 | p99 | p99.9 | Max | Total | Errors | Memory |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{table_rows}
"""
    summary_path = RESULTS_DIR / "Summary.md"
    summary_path.write_text(content, encoding="utf-8")
    return summary_path


def print_result_console(result: BenchmarkResult) -> None:
    """Pretty-print a single result to the console."""
    eco_name = ECOSYSTEMS.get(
        result.ecosystem, Ecosystem(result.ecosystem, result.ecosystem, 0, "")
    ).display_name

    if not result.success:
        print(
            f"  ✗ {eco_name} / {result.scenario} [{result.client}] — FAILED: {result.error}"
        )
        return

    status = "✓" if result.error_count == 0 else "⚠"
    mem = result.memory.mem_usage or "N/A"

    print(
        f"  {status} {eco_name:<20} {result.scenario:<18} [{result.client:<8}] "
        f"{result.requests_per_sec:>10,.2f} req/s  "
        f"p50={result.p50_ms:>7.2f}ms  "
        f"p95={result.p95_ms:>7.2f}ms  "
        f"p99={result.p99_ms:>7.2f}ms  "
        f"max={result.max_ms:>7.2f}ms  "
        f"mem={mem:>10}"
    )


def print_summary_table(results: list[BenchmarkResult]) -> None:
    """Print a sorted summary table to the console."""
    succeeded = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    if succeeded:
        succeeded.sort(key=lambda r: r.requests_per_sec, reverse=True)
        print(f"\n{'─' * 110}")
        print(
            f"  {'Ecosystem':<20} {'Scenario':<18} {'Client':<10} {'Req/sec':>10}  {'p50':>8}  {'p95':>8}  {'p99':>8}  {'max':>8}  {'Memory':>10}"
        )
        print(f"  {'─' * 110}")
        for r in succeeded:
            eco_name = ECOSYSTEMS.get(
                r.ecosystem, Ecosystem(r.ecosystem, r.ecosystem, 0, "")
            ).display_name
            mem = r.memory.mem_usage or "N/A"
            print(
                f"  {eco_name:<20} {r.scenario:<18} {r.client:<10} "
                f"{r.requests_per_sec:>10,.2f}  "
                f"{r.p50_ms:>7.2f}ms "
                f"{r.p95_ms:>7.2f}ms "
                f"{r.p99_ms:>7.2f}ms "
                f"{r.max_ms:>7.2f}ms "
                f"{mem:>10}"
            )

    if failed:
        print(f"\n  ✗ Failed ({len(failed)}):")
        for r in failed:
            eco_name = ECOSYSTEMS.get(
                r.ecosystem, Ecosystem(r.ecosystem, r.ecosystem, 0, "")
            ).display_name
            print(f"    {eco_name} / {r.scenario} [{r.client}]: {r.error}")
