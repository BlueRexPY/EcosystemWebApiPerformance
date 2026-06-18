"""Metrics collection, percentile calculation, and result dataclasses."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Sequence

# ── Percentile helpers ─────────────────────────────────────────────────────────


def percentiles(
    values: Sequence[float],
    ps: tuple[float, ...] = (50.0, 75.0, 90.0, 95.0, 99.0, 99.9),
) -> dict[str, float]:
    """Compute multiple percentiles from a list of floats.

    Uses linear interpolation (same as most monitoring systems).
    Returns dict like {"p50": 1.23, "p75": 3.45, ...}.
    Handles edge cases: empty list, single value.
    """
    if not values:
        return {f"p{int(p)}" if p == int(p) else f"p{p}": 0.0 for p in ps}

    n = len(values)
    sorted_vals = sorted(values)

    result: dict[str, float] = {}
    for p in ps:
        k = (p / 100.0) * (n - 1)
        lo = int(math.floor(k))
        hi = int(math.ceil(k))
        if lo == hi or hi >= n:
            result[_p_key(p)] = sorted_vals[min(lo, n - 1)]
        else:
            frac = k - lo
            result[_p_key(p)] = sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac
    return result


def _p_key(p: float) -> str:
    """Format percentile key: 50.0 -> 'p50', 99.9 -> 'p999'."""
    if p == int(p):
        return f"p{int(p)}"
    return f"p{int(p)}{int((p - int(p)) * 10)}"


# ── Result dataclasses ─────────────────────────────────────────────────────────


@dataclass
class MemoryStats:
    """Container resource usage from docker stats."""

    mem_usage: str = ""  # e.g. "45.2MiB"
    mem_limit: str = ""  # e.g. "1GiB"
    mem_percent: str = ""  # e.g. "4.41%"
    cpu_percent: str = ""  # e.g. "150.2%"
    pids: int = 0


@dataclass
class BenchmarkResult:
    """Complete result from a single scenario run."""

    ecosystem: str
    scenario: str
    client: str  # "wrk" | "k6" | "py-async"
    success: bool
    error: str = ""

    # ── Throughput ──
    total_requests: int = 0
    requests_per_sec: float = 0.0
    duration_seconds: float = 0.0

    # ── Latency (milliseconds) ──
    avg_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    stdev_ms: float = 0.0
    p50_ms: float = 0.0
    p75_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    p999_ms: float = 0.0

    # ── Status codes ──
    status_codes: dict[int, int] = field(default_factory=dict)  # {200: 99999, ...}
    error_count: int = 0

    # ── Resource usage ──
    memory: MemoryStats = field(default_factory=MemoryStats)

    # ── Raw output ──
    raw_output: str = ""

    @classmethod
    def from_latency_samples(
        cls,
        ecosystem: str,
        scenario: str,
        client: str,
        latency_ms_list: list[float],
        total_requests: int,
        duration_seconds: float,
        status_codes: dict[int, int],
        memory: MemoryStats,
        error_count: int = 0,
        raw_output: str = "",
    ) -> BenchmarkResult:
        """Construct a result from raw latency samples — full percentile coverage."""
        if not latency_ms_list:
            return cls(
                ecosystem=ecosystem,
                scenario=scenario,
                client=client,
                success=False,
                error="No latency samples collected",
            )

        ps = percentiles(latency_ms_list)
        return cls(
            ecosystem=ecosystem,
            scenario=scenario,
            client=client,
            success=True,
            total_requests=total_requests,
            requests_per_sec=(
                total_requests / duration_seconds if duration_seconds > 0 else 0.0
            ),
            duration_seconds=duration_seconds,
            avg_ms=statistics.mean(latency_ms_list),
            min_ms=min(latency_ms_list),
            max_ms=max(latency_ms_list),
            stdev_ms=(
                statistics.stdev(latency_ms_list) if len(latency_ms_list) > 1 else 0.0
            ),
            p50_ms=ps.get("p50", 0.0),
            p75_ms=ps.get("p75", 0.0),
            p90_ms=ps.get("p90", 0.0),
            p95_ms=ps.get("p95", 0.0),
            p99_ms=ps.get("p99", 0.0),
            p999_ms=ps.get("p999", 0.0),
            status_codes=status_codes,
            error_count=error_count,
            memory=memory,
            raw_output=raw_output,
        )

    def latency_summary(self) -> str:
        """One-line latency summary for console output."""
        return (
            f"avg={self.avg_ms:.2f}ms "
            f"p50={self.p50_ms:.2f}ms "
            f"p95={self.p95_ms:.2f}ms "
            f"p99={self.p99_ms:.2f}ms "
            f"max={self.max_ms:.2f}ms"
        )
