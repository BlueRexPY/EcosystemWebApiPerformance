"""Markdown and console output formatters for benchmark results."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    ECOSYSTEMS,
    PROJECT_ROOT,
    SCENARIOS,
    Ecosystem,
    Scenario,
    result_path,
)
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
    """Generate a combined summary markdown, merging with any existing results."""
    from .config import RESULTS_DIR

    _ensure_dir(RESULTS_DIR / ".keep")

    # Merge with existing: key = (ecosystem, scenario, client)
    merged: dict[tuple[str, str, str], str] = {}

    summary_path = RESULTS_DIR / "Summary.md"
    if summary_path.exists():
        existing = summary_path.read_text(encoding="utf-8")
        for line in existing.split("\n"):
            if (
                line.startswith("| ")
                and " | " in line
                and not line.startswith("| Ecosystem")
            ):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 3:
                    merged[(parts[0], parts[1], parts[2])] = line

    for r in results:
        eco_name = ECOSYSTEMS.get(
            r.ecosystem, Ecosystem(r.ecosystem, r.ecosystem, 0, "")
        ).display_name
        mem = r.memory.mem_usage or "N/A"
        rps = f"{r.requests_per_sec:,.2f}" if r.success else "FAILED"
        merged[(eco_name, r.scenario, r.client)] = (
            f"| {eco_name} | {r.scenario} | {r.client} | {rps} | "
            f"{r.avg_ms:.2f}ms | {r.p50_ms:.2f}ms | {r.p95_ms:.2f}ms | "
            f"{r.p99_ms:.2f}ms | {r.p999_ms:.2f}ms | {r.max_ms:.2f}ms | "
            f"{r.total_requests:,} | {r.error_count} | {mem} |"
        )

    table_rows = "\n".join(merged.values())

    content = f"""# {title}

**Generated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}

## Results

| Ecosystem | Scenario | Client | Req/sec | Avg | p50 | p95 | p99 | p99.9 | Max | Total | Errors | Memory |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{table_rows}
"""
    summary_path.write_text(content, encoding="utf-8")
    return summary_path


def update_readme(summary_path: Path) -> None:
    """Inject the latest Summary.md table into README.md between <!-- SUMMARY --> markers."""
    readme_path = PROJECT_ROOT / "README.md"
    if not readme_path.exists():
        return

    summary_text = summary_path.read_text(encoding="utf-8")

    # Extract the table rows (skip header lines)
    table_match = re.search(r"\| (.+?)\n\n", summary_text, re.DOTALL)
    if not table_match:
        return

    # Build the summary section
    lines = summary_text.split("\n")
    table_started = False
    table_rows: list[str] = []
    for line in lines:
        if line.startswith("| Ecosystem"):
            table_started = True
            table_rows.append(line)
            continue
        if table_started:
            if line.startswith("|"):
                table_rows.append(line)
            elif not line.strip():
                break

    # Keep header + first separator, then all data rows sorted
    header = table_rows[0]
    separator = table_rows[1]
    data_rows = sorted(table_rows[2:], key=lambda r: _parse_rps(r), reverse=True)

    summary_block = f"\n| Ecosystem | Scenario | Client | Req/sec | Avg | p50 | p95 | p99 | p99.9 | Max | Total | Errors | Memory |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    summary_block += "\n".join(data_rows)
    summary_block += "\n"

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    replacement = f"<!-- SUMMARY -->\n**Generated**: {generated}\n\n{summary_block}\n<!-- /SUMMARY -->"

    readme_content = readme_path.read_text(encoding="utf-8")
    new_content = re.sub(
        r"<!-- SUMMARY -->.*<!-- /SUMMARY -->",
        replacement,
        readme_content,
        flags=re.DOTALL,
    )
    readme_path.write_text(new_content, encoding="utf-8")


def _parse_rps(row: str) -> float:
    """Extract req/sec from a summary table row for sorting."""
    parts = [p.strip() for p in row.split("|") if p.strip()]
    if len(parts) >= 4:
        try:
            return float(parts[3].replace(",", ""))
        except (ValueError, IndexError):
            pass
    return 0.0


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
