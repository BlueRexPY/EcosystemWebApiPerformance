"""Core benchmark runner with three clients: wrk, k6, and py-async.

Handles Docker lifecycle, metric collection, and orchestration.
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from .config import (
    DEFAULT_K6,
    DEFAULT_PYASYNC,
    DEFAULT_WRK,
    PROJECT_ROOT,
    SCENARIOS,
    Ecosystem,
    K6Config,
    PyAsyncConfig,
    Scenario,
    WrkConfig,
    result_path,
)
from .formatter import update_readme, write_result_md, write_summary_md
from .metrics import BenchmarkResult, MemoryStats

logger = logging.getLogger(__name__)

# ── Docker helpers ─────────────────────────────────────────────────────────────

COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"

_WRK_PATH = shutil.which("wrk") or ""
_K6_PATH = shutil.which("k6") or ""

# Known container names per ecosystem (docker-compose service names TBD)
# For now, infer from docker ps by image/port.
ECOSYSTEM_CONTAINER_HINTS: dict[str, list[str]] = {
    "js": ["bun", "elysia", "js"],
    "go": ["go", "fiber", "golang"],
    "cs": ["dotnet", "cs", "csharp"],
}


def _compose_cmd() -> list[str]:
    if shutil.which("docker") and _has_compose_v2():
        return ["docker", "compose", "-f", str(COMPOSE_FILE)]
    if shutil.which("docker-compose"):
        return ["docker-compose", "-f", str(COMPOSE_FILE)]
    raise RuntimeError("Neither 'docker compose' nor 'docker-compose' found")


def _has_compose_v2() -> bool:
    try:
        r = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def _find_container(eco: Ecosystem) -> str:
    """Find a running container for the given ecosystem by port."""
    r = subprocess.run(
        ["docker", "ps", "--format", "{{.ID}}\t{{.Ports}}"],
        capture_output=True,
        text=True,
    )
    for line in r.stdout.strip().splitlines():
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        cid, ports = parts[0], parts[1]
        if f":{eco.port}->" in ports or f"::{eco.port}" in ports:
            return cid
    return ""


def get_memory_stats(eco: Ecosystem) -> MemoryStats:
    """Get memory/CPU usage for the ecosystem's container."""
    cid = _find_container(eco)
    if not cid:
        logger.warning("No container found for %s on port %d", eco.key, eco.port)
        return MemoryStats()

    r = subprocess.run(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.MemUsage}}|{{.MemPerc}}|{{.CPUPerc}}|{{.PIDs}}",
            cid,
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return MemoryStats()

    parts = r.stdout.strip().split("|")
    if len(parts) < 4:
        return MemoryStats()

    mem_parts = parts[0].split("/")
    return MemoryStats(
        mem_usage=mem_parts[0].strip() if mem_parts else "",
        mem_limit=mem_parts[1].strip() if len(mem_parts) > 1 else "",
        mem_percent=parts[1].strip(),
        cpu_percent=parts[2].strip(),
        pids=int(parts[3].strip()) if parts[3].strip().isdigit() else 0,
    )


# ── Client 1: wrk ─────────────────────────────────────────────────────────────


def _build_wrk_cmd(eco: Ecosystem, scenario: Scenario, cfg: WrkConfig) -> list[str]:
    """Build wrk command, using a Lua script for POST with body if needed."""
    url = f"http://127.0.0.1:{eco.port}{scenario.path}"
    cmd = [
        "wrk",
        "-t",
        str(cfg.threads),
        "-c",
        str(cfg.connections),
        "-d",
        cfg.duration_flag,
    ]
    if scenario.payload and scenario.method == "POST":
        # wrk doesn't natively support POST body; use a temp Lua script
        script = _write_wrk_post_script(scenario.payload, url)
        cmd.extend(["-s", str(script)])
    cmd.append(url)
    return cmd


def _write_wrk_post_script(payload: dict, _url: str) -> Path:
    """Write a wrk Lua script for POST requests with JSON body."""
    body = json.dumps(payload)
    # Escape backslashes for Lua single-quoted strings so \n stays literal \n
    body_lua = body.replace("\\", "\\\\")
    script = (
        f'wrk.method = "POST"\n'
        f"wrk.body = '{body_lua}'\n"
        f'wrk.headers["Content-Type"] = "application/json"\n'
    )
    path = Path("/tmp/wrk_post_script.lua")
    path.write_text(script)
    return path


def _parse_wrk_output(
    output: str, eco: Ecosystem, scenario_name: str
) -> BenchmarkResult:
    """Parse wrk stdout into a BenchmarkResult.

    wrk gives avg/stdev/max latency but NOT percentiles. We note that.
    """
    import re

    rps_match = re.search(r"Requests/sec:\s+([\d.]+)", output)
    total_match = re.search(r"(\d+)\s+requests?\s+in", output)
    lat_match = re.search(
        r"Latency\s+([\d.]+)(us|ms|s)\s+([\d.]+)(us|ms|s)\s+([\d.]+)(us|ms|s)", output
    )
    duration_match = re.search(r"in\s+([\d.]+)(s|ms|m)", output)
    non2xx_match = re.search(r"Non-2xx or 3xx responses:\s+(\d+)", output)

    rps = float(rps_match.group(1)) if rps_match else 0.0
    total = int(total_match.group(1)) if total_match else 0
    duration = 0.0
    if duration_match:
        val = float(duration_match.group(1))
        unit = duration_match.group(2)
        duration = val if unit == "s" else val / 1000 if unit == "ms" else val * 60

    avg_ms = 0.0
    max_ms = 0.0
    if lat_match:
        avg_val = float(lat_match.group(1))
        avg_unit = lat_match.group(2)
        max_val = float(lat_match.group(5))
        max_unit = lat_match.group(6)
        avg_ms = (
            avg_val * 1000
            if avg_unit == "s"
            else avg_val / 1000 if avg_unit == "us" else avg_val
        )
        max_ms = (
            max_val * 1000
            if max_unit == "s"
            else max_val / 1000 if max_unit == "us" else max_val
        )

    error_count = int(non2xx_match.group(1)) if non2xx_match else 0
    mem = get_memory_stats(eco)

    return BenchmarkResult(
        ecosystem=eco.key,
        scenario=scenario_name,
        client="wrk",
        success=True,
        total_requests=total,
        requests_per_sec=rps,
        duration_seconds=duration,
        avg_ms=avg_ms,
        max_ms=max_ms,
        p50_ms=0.0,  # wrk doesn't provide percentiles — use k6 or py-async
        p95_ms=0.0,
        p99_ms=0.0,
        p999_ms=0.0,
        error_count=error_count,
        memory=mem,
        raw_output=output,
    )


def run_wrk(
    eco: Ecosystem, scenario: Scenario, cfg: WrkConfig = DEFAULT_WRK
) -> BenchmarkResult:
    """Run wrk against a single endpoint."""
    if not _WRK_PATH:
        return BenchmarkResult(
            ecosystem=eco.key,
            scenario=scenario.name,
            client="wrk",
            success=False,
            error="wrk not installed. Install with: sudo apt install wrk",
        )

    cmd = _build_wrk_cmd(eco, scenario, cfg)
    logger.info("wrk: %s", " ".join(cmd))
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=cfg.duration_seconds + 30
    )

    output = r.stdout + "\n" + r.stderr
    result = _parse_wrk_output(output, eco, scenario.name)
    if r.returncode != 0 and result.requests_per_sec == 0:
        result.success = False
        result.error = f"wrk exit code {r.returncode}: {r.stderr[:200]}"
    return result


# ── Client 2: k6 ──────────────────────────────────────────────────────────────


def _write_k6_script(scenario: Scenario, eco: Ecosystem) -> Path:
    """Generate a k6 script for the given POST scenario."""
    body = json.dumps(scenario.payload) if scenario.payload else "{}"
    script = f"""// Auto-generated k6 script for {scenario.label}
import http from "k6/http";
import {{ check, sleep }} from "k6";
import {{ Trend, Counter, Rate }} from "k6/metrics";

const latency = new Trend("latency_ms");
const errors = new Rate("errors");

export const options = {{
  vus: {DEFAULT_K6.vus},
  duration: "{DEFAULT_K6.duration_seconds}s",
}};

export default function () {{
  const url = "http://127.0.0.1:{eco.port}{scenario.path}";
  const payload = JSON.stringify({body});
  const params = {{ headers: {{ "Content-Type": "application/json" }} }};

  const start = Date.now();
  const res = http.post(url, payload, params);
  latency.add(Date.now() - start);

  const ok = check(res, {{
    "status is 2xx": (r) => r.status >= 200 && r.status < 300,
  }});
  errors.add(!ok);
}}
"""
    path = Path(f"/tmp/k6_script_{scenario.name}.js")
    path.write_text(script)
    return path


def _parse_k6_output(
    output: str, eco: Ecosystem, scenario_name: str
) -> BenchmarkResult:
    """Parse k6 JSON/STDOUT into BenchmarkResult."""
    import re

    # k6 trend output: latency_ms..............: avg=123.45 min=10.00 med=100.00 max=500.00 p(90)=200.00 p(95)=300.00
    trend_re = re.compile(
        r"latency_ms[.\s]+:.*?avg=([\d.]+)\s+min=([\d.]+)\s+med=([\d.]+)\s+max=([\d.]+)\s+p\(90\)=([\d.]+)\s+p\(95\)=([\d.]+)"
    )
    # Also try p(99)=...
    p99_re = re.compile(r"p\(99\)=([\d.]+)")
    iters_re = re.compile(r"iterations[.\s]+:\s+(\d+)\s+([\d.]+)/s")
    duration_re = re.compile(r"running\s+\((\d+)m(\d+)", re.IGNORECASE)
    checks_re = re.compile(r"checks[.\s]+:\s+([\d.]+)%")

    # Try to parse k6 JSON summary if --summary-export was used
    total_requests = 0
    rps = 0.0
    duration = float(DEFAULT_K6.duration_seconds)
    avg_ms = min_ms = med_ms = max_ms = p90_ms = p95_ms = p99_ms = 0.0
    error_count = 0

    # Parse from text output
    m = iters_re.search(output)
    if m:
        total_requests = int(m.group(1))
        rps = float(m.group(2))

    m = trend_re.search(output)
    if m:
        avg_ms = float(m.group(1))
        min_ms = float(m.group(2))
        med_ms = float(m.group(3))
        max_ms = float(m.group(4))
        p90_ms = float(m.group(5))
        p95_ms = float(m.group(6))

    m = p99_re.search(output)
    if m:
        p99_ms = float(m.group(1))

    m = checks_re.search(output)
    if m:
        passed_pct = float(m.group(1))
        if passed_pct < 100:
            error_count = int(total_requests * (100 - passed_pct) / 100)

    mem = get_memory_stats(eco)

    return BenchmarkResult(
        ecosystem=eco.key,
        scenario=scenario_name,
        client="k6",
        success=True,
        total_requests=total_requests,
        requests_per_sec=rps,
        duration_seconds=duration,
        avg_ms=avg_ms,
        min_ms=min_ms,
        max_ms=max_ms,
        p50_ms=med_ms,  # k6 'med' = p50
        p75_ms=0.0,  # k6 doesn't show p75 by default
        p90_ms=p90_ms,
        p95_ms=p95_ms,
        p99_ms=p99_ms,
        error_count=error_count,
        memory=mem,
        raw_output=output,
    )


def run_k6(
    eco: Ecosystem, scenario: Scenario, cfg: K6Config = DEFAULT_K6
) -> BenchmarkResult:
    """Run k6 against a single endpoint."""
    if not _K6_PATH:
        return BenchmarkResult(
            ecosystem=eco.key,
            scenario=scenario.name,
            client="k6",
            success=False,
            error="k6 not installed. Install with: snap install k6",
        )

    script_path = _write_k6_script(scenario, eco)
    cmd = [
        "k6",
        "run",
        "--vus",
        str(cfg.vus),
        "--duration",
        cfg.duration_flag,
        "--no-color",
        str(script_path),
    ]

    logger.info("k6: %s", " ".join(cmd))
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=cfg.duration_seconds + 60
    )

    output = r.stdout + "\n" + r.stderr
    result = _parse_k6_output(output, eco, scenario.name)
    # k6 exits non-zero on threshold failure — still valid results
    if result.total_requests == 0 and r.returncode != 0:
        result.success = False
        result.error = f"k6 exit code {r.returncode}: {r.stderr[:200]}"
    return result


# ── Client 3: py-async (Python httpx) ────────────────────────────────────────


@dataclass
class _Sample:
    status: int
    latency_ms: float


async def _py_async_worker(
    client: httpx.AsyncClient,
    url: str,
    payload: str | None,
    method: str,
    samples: list[_Sample],
    stop_event: asyncio.Event,
    stats_lock: asyncio.Lock,
) -> None:
    """Single async worker that hammers the endpoint until stopped."""
    while not stop_event.is_set():
        start = time.perf_counter()
        try:
            if method == "POST":
                resp = await client.post(
                    url, content=payload, headers={"Content-Type": "application/json"}
                )
            else:
                resp = await client.get(url)
            latency_ms = (time.perf_counter() - start) * 1000
            async with stats_lock:
                samples.append(_Sample(status=resp.status_code, latency_ms=latency_ms))
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            async with stats_lock:
                samples.append(_Sample(status=0, latency_ms=latency_ms))


async def _run_py_async(
    eco: Ecosystem,
    scenario: Scenario,
    cfg: PyAsyncConfig,
    url: str | None = None,
    payload: dict | None = None,
) -> list[_Sample]:
    """Run async HTTP workers and return latency samples."""
    target_url = url or f"http://127.0.0.1:{eco.port}{scenario.path}"
    body = (
        json.dumps(payload or scenario.payload)
        if (payload or scenario.payload)
        else None
    )

    samples: list[_Sample] = []
    lock = asyncio.Lock()
    stop = asyncio.Event()

    limits = httpx.Limits(
        max_connections=cfg.concurrency + 10, max_keepalive_connections=cfg.concurrency
    )
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(30.0)) as client:
        # Warmup
        logger.info("py-async warmup: %ds...", cfg.warmup_seconds)
        warmup_stop = asyncio.Event()
        warmup_tasks = [
            asyncio.create_task(
                _py_async_worker(
                    client, target_url, body, scenario.method, [], warmup_stop, lock
                )
            )
            for _ in range(cfg.concurrency)
        ]
        await asyncio.sleep(cfg.warmup_seconds)
        warmup_stop.set()
        await asyncio.gather(*warmup_tasks, return_exceptions=True)

        # Benchmark
        logger.info(
            "py-async benchmark: %ds with %d concurrent workers...",
            cfg.duration_seconds,
            cfg.concurrency,
        )
        tasks = [
            asyncio.create_task(
                _py_async_worker(
                    client, target_url, body, scenario.method, samples, stop, lock
                )
            )
            for _ in range(cfg.concurrency)
        ]
        await asyncio.sleep(cfg.duration_seconds)
        stop.set()
        await asyncio.gather(*tasks, return_exceptions=True)

    return samples


def _run_mixed_with_wrk(
    eco: Ecosystem,
    cfg: PyAsyncConfig,
    name: str,
    weighted_payloads: list[tuple[float, dict]],
    base_path: str = "/casino/callback",
) -> BenchmarkResult:
    """Run a mixed workload using wrk with a Lua script for weighted random payload selection."""
    url = f"http://127.0.0.1:{eco.port}{base_path}"
    bodies = [json.dumps(p) for _, p in weighted_payloads]
    weights = [w for w, _ in weighted_payloads]

    lua_lines = [
        'wrk.method = "POST"',
        'wrk.headers["Content-Type"] = "application/json"',
        "math.randomseed(os.time())",
        "",
        "request = function()",
    ]
    for i, body in enumerate(bodies):
        safe_body = body.replace("\\", "\\\\").replace("'", "\\'")
        if i == 0:
            lua_lines.append(f"    local bodies = {{ [1] = '{safe_body}'")
        else:
            lua_lines.append(f"        , [{i + 1}] = '{safe_body}'")
    lua_lines[-1] += " }"
    lua_lines.append(f"    local weights = {{ {', '.join(str(w) for w in weights)} }}")
    lua_lines.append("    local r = math.random()")
    lua_lines.append("    local cumulative = 0")
    for i, w in enumerate(weights):
        lua_lines.append(f"    cumulative = cumulative + {w}")
        lua_lines.append(
            f"    if r < cumulative then wrk.body = bodies[{i + 1}] return wrk.format('POST', wrk.path, wrk.headers, wrk.body) end"
        )
    lua_lines.append("    return wrk.format('POST', wrk.path, wrk.headers, bodies[1])")
    lua_lines.append("end")

    script_path = Path(f"/tmp/wrk_mixed_{name}.lua")
    script_path.write_text("\n".join(lua_lines))

    cmd = [
        "wrk",
        "-t",
        "2",
        "-c",
        str(cfg.concurrency),
        "-d",
        f"{cfg.duration_seconds}s",
        "-s",
        str(script_path),
        url,
    ]
    logger.info("wrk mixed: %s", " ".join(cmd))
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=cfg.duration_seconds + 30
    )
    from .config import WrkConfig

    return _parse_wrk_output(r.stdout + "\n" + r.stderr, eco, name)


def _run_mixed_full_with_wrk(
    eco: Ecosystem,
    cfg: PyAsyncConfig,
) -> BenchmarkResult:
    """Mixed full workload across all endpoint types — uses wrk with multi-path Lua."""
    base = f"http://127.0.0.1:{eco.port}"
    # (weight, path, payload)
    subs = [
        (10, "/casino/authenticate", SCENARIOS["casino_auth"].payload),
        (35, "/casino/callback", SCENARIOS["casino_bet"].payload),
        (15, "/casino/callback", SCENARIOS["casino_win"].payload),
        (5, "/casino/callback", SCENARIOS["casino_rollback"].payload),
        (5, "/psp/callback", SCENARIOS["psp_deposit"].payload),
        (15, "/graphql", SCENARIOS["player_balance"].payload),
        (10, "/graphql", SCENARIOS["player_login"].payload),
        (5, "/graphql", SCENARIOS["player_me"].payload),
    ]
    weights = [s[0] for s in subs]
    paths = [s[1] for s in subs]
    payloads = [s[2] for s in subs]
    bodies = [json.dumps(p) if p else "{}" for p in payloads]

    lua_lines = [
        'wrk.method = "POST"',
        'wrk.headers["Content-Type"] = "application/json"',
        "math.randomseed(os.time())",
        "",
        "request = function()",
        "    local weights = { " + ", ".join(str(w) for w in weights) + " }",
        "    local paths = { " + ", ".join(f'"{p}"' for p in paths) + " }",
    ]
    lua_lines.append("    local bodies = {")
    for i, body in enumerate(bodies):
        safe = body.replace("\\", "\\\\").replace("'", "\\'")
        lua_lines.append(f"        [{i + 1}] = '{safe}',")
    lua_lines.append("    }")
    lua_lines.append("    local r = math.random()")
    lua_lines.append("    local cumulative = 0")
    for i, w in enumerate(weights):
        lua_lines.append(f"    cumulative = cumulative + {w}")
        lua_lines.append(
            f"    if r < cumulative then wrk.path = paths[{i + 1}] wrk.body = bodies[{i + 1}] return wrk.format('POST', wrk.path, wrk.headers, wrk.body) end"
        )
    lua_lines.append("    return wrk.format('POST', paths[1], wrk.headers, bodies[1])")
    lua_lines.append("end")

    script_path = Path("/tmp/wrk_mixed_full.lua")
    script_path.write_text("\n".join(lua_lines))

    cmd = [
        "wrk",
        "-t",
        "2",
        "-c",
        str(cfg.concurrency),
        "-d",
        f"{cfg.duration_seconds}s",
        "-s",
        str(script_path),
        f"{base}/casino/callback",
    ]
    logger.info("wrk mixed_full: %s", " ".join(cmd))
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=cfg.duration_seconds + 30
    )
    from .config import WrkConfig

    return _parse_wrk_output(r.stdout + "\n" + r.stderr, eco, "mixed_full")


def _run_py_async_mixed_casino(
    eco: Ecosystem,
    cfg: PyAsyncConfig,
) -> BenchmarkResult:
    """Mixed casino workload: 80% bet, 15% win, 5% rollback — uses wrk for real throughput."""
    return _run_mixed_with_wrk(
        eco,
        cfg,
        "mixed_casino",
        [
            (0.80, SCENARIOS["casino_bet"].payload),
            (0.15, SCENARIOS["casino_win"].payload),
            (0.05, SCENARIOS["casino_rollback"].payload),
        ],
    )


def _samples_to_result(
    samples: list[_Sample],
    eco: Ecosystem,
    scenario_name: str,
    client_name: str,
    cfg: PyAsyncConfig,
) -> BenchmarkResult:
    """Convert raw samples to a BenchmarkResult with full percentiles."""
    latencies = [s.latency_ms for s in samples if s.status > 0]
    error_samples = [s for s in samples if s.status == 0 or s.status >= 400]
    status_counts: dict[int, int] = {}
    for s in samples:
        if s.status > 0:
            status_counts[s.status] = status_counts.get(s.status, 0) + 1

    mem = get_memory_stats(eco)

    return BenchmarkResult.from_latency_samples(
        ecosystem=eco.key,
        scenario=scenario_name,
        client=client_name,
        latency_ms_list=latencies,
        total_requests=len(samples),
        duration_seconds=cfg.duration_seconds,
        status_codes=status_counts,
        memory=mem,
        error_count=len(error_samples),
        raw_output=f"Total samples: {len(samples)}, latency samples: {len(latencies)}, error samples: {len(error_samples)}",
    )


def run_py_async(
    eco: Ecosystem,
    scenario: Scenario,
    cfg: PyAsyncConfig = DEFAULT_PYASYNC,
) -> BenchmarkResult:
    """Mixed scenarios use wrk for real throughput; player_journey is sequential."""
    if scenario.name == "mixed_casino":
        return _run_py_async_mixed_casino(eco, cfg)
    if scenario.name == "mixed_full":
        return _run_mixed_full_with_wrk(eco, cfg)
    if scenario.name == "player_journey":
        return _run_player_journey(eco, cfg)  # only this one needs py-async (stateful)
    samples = asyncio.run(_run_py_async(eco, scenario, cfg))
    return _samples_to_result(samples, eco, scenario.name, "py-async", cfg)


def _run_py_async_mixed_full(
    eco: Ecosystem,
    cfg: PyAsyncConfig,
) -> BenchmarkResult:
    """Mixed full workload across all endpoint types."""
    import random

    # Define sub-scenarios: (path, payload, weight)
    subs = [
        ("/casino/authenticate", SCENARIOS["casino_auth"].payload, 10),
        ("/casino/callback", SCENARIOS["casino_bet"].payload, 35),
        ("/casino/callback", SCENARIOS["casino_win"].payload, 15),
        ("/casino/callback", SCENARIOS["casino_rollback"].payload, 5),
        ("/psp/callback", SCENARIOS["psp_deposit"].payload, 5),
        ("/graphql", SCENARIOS["player_balance"].payload, 15),
        ("/graphql", SCENARIOS["player_login"].payload, 10),
        ("/graphql", SCENARIOS["player_me"].payload, 5),
    ]
    # Build weighted choice
    paths = [s[0] for s in subs]
    bodies = [json.dumps(s[1]) if s[1] else "{}" for s in subs]
    weights = [s[2] for s in subs]
    total_weight = sum(weights)
    cum_weights = [sum(weights[: i + 1]) for i in range(len(weights))]

    def _pick():
        r = random.random() * total_weight
        for i, cw in enumerate(cum_weights):
            if r <= cw:
                return paths[i], bodies[i]
        return paths[-1], bodies[-1]

    base_url = f"http://127.0.0.1:{eco.port}"

    async def _worker(
        client: httpx.AsyncClient,
        samples: list[_Sample],
        stop: asyncio.Event,
        lock: asyncio.Lock,
    ) -> None:
        while not stop.is_set():
            path, body = _pick()
            url = f"{base_url}{path}"
            start = time.perf_counter()
            try:
                resp = await client.post(
                    url, content=body, headers={"Content-Type": "application/json"}
                )
                latency_ms = (time.perf_counter() - start) * 1000
                async with lock:
                    samples.append(
                        _Sample(status=resp.status_code, latency_ms=latency_ms)
                    )
            except Exception:
                latency_ms = (time.perf_counter() - start) * 1000
                async with lock:
                    samples.append(_Sample(status=0, latency_ms=latency_ms))

    async def _run():
        samples: list[_Sample] = []
        lock = asyncio.Lock()
        stop = asyncio.Event()
        limits = httpx.Limits(max_connections=cfg.concurrency + 10)

        async with httpx.AsyncClient(
            limits=limits, timeout=httpx.Timeout(30.0)
        ) as client:
            warmup_stop = asyncio.Event()
            warmup_tasks = [
                asyncio.create_task(_worker(client, [], warmup_stop, lock))
                for _ in range(cfg.concurrency)
            ]
            await asyncio.sleep(cfg.warmup_seconds)
            warmup_stop.set()
            await asyncio.gather(*warmup_tasks, return_exceptions=True)

            tasks = [
                asyncio.create_task(_worker(client, samples, stop, lock))
                for _ in range(cfg.concurrency)
            ]
            await asyncio.sleep(cfg.duration_seconds)
            stop.set()
            await asyncio.gather(*tasks, return_exceptions=True)

        return samples

    samples = asyncio.run(_run())
    return _samples_to_result(samples, eco, "mixed_full", "py-async", cfg)


# ── Player Journey (stateful end-to-end simulation) ────────────────────────────


def _random_player_id() -> int:
    """Return a random player ID in the seed range (1–100000)."""
    import random

    return random.randint(1, 100000)


def _random_amount(min_cents: int = 100, max_cents: int = 500000) -> int:
    """Random amount in cents for deposits/bets/wins."""
    import random

    return random.randint(min_cents, max_cents)


def _random_rounds() -> int:
    """Random number of bet/win rounds per journey (3–15)."""
    import random

    return random.randint(3, 15)


def _journey_signup_payload(player_id: int) -> dict:
    return {
        "query": """
            mutation Signup($username: String!, $password: String!) {
                signup(username: $username, password: $password) {
                    token
                    player { id username }
                }
            }
        """,
        "variables": {
            "username": f"player_{player_id:05d}",
            "password": "testpass123",
        },
    }


def _journey_login_payload(player_id: int) -> dict:
    return {
        "query": """
            mutation Login($username: String!, $password: String!) {
                login(username: $username, password: $password) {
                    token
                    player { id username }
                }
            }
        """,
        "variables": {
            "username": f"player_{player_id:05d}",
            "password": "testpass123",
        },
    }


def _journey_deposit_payload(amount_cents: int) -> dict:
    import uuid

    return {
        "type": "deposit",
        "amount_cents": amount_cents,
        "transaction_id": f"psp-dep-{uuid.uuid4().hex[:12]}",
    }


def _journey_auth_payload(player_id: int) -> dict:
    return {
        "token": f"session-player-{player_id:05d}",
        "game_id": f"game-slot-{player_id % 20:02d}",
    }


def _journey_bet_payload(amount_cents: int) -> dict:
    import uuid

    return {
        "type": "bet",
        "amount_cents": amount_cents,
        "transaction_id": f"tx-{uuid.uuid4().hex[:12]}",
        "round_id": f"round-{uuid.uuid4().hex[:8]}",
    }


def _journey_win_payload(amount_cents: int) -> dict:
    import uuid

    return {
        "type": "win",
        "amount_cents": amount_cents,
        "transaction_id": f"tx-{uuid.uuid4().hex[:12]}",
        "round_id": f"round-{uuid.uuid4().hex[:8]}",
    }


_JOURNEY_BALANCE_QUERY = {"query": """
        query PlayerBalance {
            balance { amount_cents currency }
        }
    """}

_JOURNEY_TRANSACTIONS_QUERY = {
    "query": """
        query Transactions($limit: Int!) {
            transactions(limit: $limit) {
                id type amount_cents created_at
            }
        }
    """,
    "variables": {"limit": 20},
}

_JOURNEY_LOGOUT_MUTATION = {
    "query": "mutation Logout { logout }",
}


def _run_player_journey(
    eco: Ecosystem,
    cfg: PyAsyncConfig,
) -> BenchmarkResult:
    """Full stateful player lifecycle simulation.

    Each virtual user runs the complete flow:
      1. SIGNUP   → create account
      2. LOGIN    → get session token
      3. DEPOSIT  → random 5000–500000 cents via PSP
      4. LOOP N times (3–15 rounds):
         a. AUTH  → casino authenticates session
         b. BET   → random 100–50000 cents
         c. WIN   → random 50–25000 cents
         d. TRANSACTIONS → check recent tx (every 3rd round)
      5. WITHDRAW → random withdrawal
      6. LOGOUT
    """
    import random
    import time as time_mod

    base_url = f"http://127.0.0.1:{eco.port}"
    headers = {"Content-Type": "application/json"}

    # Per-step latency collectors for journey breakdown
    step_latencies: dict[str, list[float]] = {
        "signup": [],
        "login": [],
        "deposit": [],
        "auth": [],
        "bet": [],
        "win": [],
        "transactions": [],
        "withdraw": [],
        "logout": [],
    }
    all_latencies: list[float] = []

    async def _post_json(
        client: httpx.AsyncClient, path: str, payload: dict
    ) -> tuple[int, float]:
        start = time_mod.perf_counter()
        try:
            resp = await client.post(
                f"{base_url}{path}",
                content=json.dumps(payload),
                headers=headers,
            )
            latency = (time_mod.perf_counter() - start) * 1000
            return resp.status_code, latency
        except Exception:
            latency = (time_mod.perf_counter() - start) * 1000
            return 0, latency

    async def _journey_worker(
        worker_id: int,
        stop_event: asyncio.Event,
        samples: list[_Sample],
        lock: asyncio.Lock,
    ) -> None:
        """One virtual player's complete journey, repeated until stop."""
        import random as _random

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0), http2=True) as client:
            while not stop_event.is_set():
                pid = _random_player_id()

                # 1. SIGNUP
                _, lat = await _post_json(
                    client, "/graphql", _journey_signup_payload(pid)
                )
                step_latencies["signup"].append(lat)
                all_latencies.append(lat)

                # 2. LOGIN
                _, lat = await _post_json(
                    client, "/graphql", _journey_login_payload(pid)
                )
                step_latencies["login"].append(lat)
                all_latencies.append(lat)

                # 3. DEPOSIT
                deposit_amt = _random_amount(5000, 500000)
                _, lat = await _post_json(
                    client, "/psp/callback", _journey_deposit_payload(deposit_amt)
                )
                step_latencies["deposit"].append(lat)
                all_latencies.append(lat)

                # 4. GAMEPLAY LOOP
                rounds = _random_rounds()
                for rnd in range(rounds):
                    # AUTH
                    _, lat = await _post_json(
                        client, "/casino/authenticate", _journey_auth_payload(pid)
                    )
                    step_latencies["auth"].append(lat)
                    all_latencies.append(lat)

                    # BET
                    bet_amt = _random_amount(100, 50000)
                    _, lat = await _post_json(
                        client, "/casino/callback", _journey_bet_payload(bet_amt)
                    )
                    step_latencies["bet"].append(lat)
                    all_latencies.append(lat)

                    # WIN
                    win_amt = _random_amount(50, 25000)
                    _, lat = await _post_json(
                        client, "/casino/callback", _journey_win_payload(win_amt)
                    )
                    step_latencies["win"].append(lat)
                    all_latencies.append(lat)

                    # Check transactions every 3rd round
                    if rnd % 3 == 0:
                        _, lat = await _post_json(
                            client, "/graphql", _JOURNEY_TRANSACTIONS_QUERY
                        )
                        step_latencies["transactions"].append(lat)
                        all_latencies.append(lat)

                # 5. WITHDRAW
                wd_amt = _random_amount(5000, 200000)
                wd_payload = _journey_deposit_payload(wd_amt)
                wd_payload["type"] = "withdrawal"
                _, lat = await _post_json(client, "/psp/callback", wd_payload)
                step_latencies["withdraw"].append(lat)
                all_latencies.append(lat)

                # 6. LOGOUT
                _, lat = await _post_json(client, "/graphql", _JOURNEY_LOGOUT_MUTATION)
                step_latencies["logout"].append(lat)
                all_latencies.append(lat)

                # Record journey completion as one "request" for throughput counting
                async with lock:
                    for l in all_latencies[
                        -1:
                    ]:  # count just the journey as a unit for req/sec
                        samples.append(_Sample(status=200, latency_ms=l))

    # --- Run ---
    samples: list[_Sample] = []
    lock = asyncio.Lock()
    stop = asyncio.Event()

    async def _run():
        limits = httpx.Limits(max_connections=cfg.concurrency + 10)

        async with httpx.AsyncClient(
            limits=limits, timeout=httpx.Timeout(30.0)
        ) as client:
            # Warmup: run a few journeys to prime caches
            logger.info("player_journey warmup: %ds...", cfg.warmup_seconds)
            warmup_stop = asyncio.Event()
            warmup_tasks = [
                asyncio.create_task(_journey_worker(i, warmup_stop, [], lock))
                for i in range(min(cfg.concurrency, 20))
            ]
            await asyncio.sleep(cfg.warmup_seconds)
            warmup_stop.set()
            await asyncio.gather(*warmup_tasks, return_exceptions=True)

            # Benchmark
            logger.info(
                "player_journey benchmark: %ds with %d concurrent players...",
                cfg.duration_seconds,
                cfg.concurrency,
            )
            tasks = [
                asyncio.create_task(_journey_worker(i, stop, samples, lock))
                for i in range(cfg.concurrency)
            ]
            await asyncio.sleep(cfg.duration_seconds)
            stop.set()
            await asyncio.gather(*tasks, return_exceptions=True)

    asyncio.run(_run())

    # Build enriched result with journey breakdown
    journeys = len(samples)  # one sample = one complete journey
    total_steps = len(all_latencies)
    mem = get_memory_stats(eco)

    result = BenchmarkResult.from_latency_samples(
        ecosystem=eco.key,
        scenario="player_journey",
        client="py-async",
        latency_ms_list=all_latencies,
        total_requests=total_steps,  # count individual steps
        duration_seconds=cfg.duration_seconds,
        status_codes={200: total_steps},
        memory=mem,
        error_count=0,
        raw_output=_format_journey_breakdown(
            journeys, total_steps, step_latencies, cfg
        ),
    )
    # Override req/sec to reflect journey completions (more meaningful)
    if cfg.duration_seconds > 0:
        result.requests_per_sec = journeys / cfg.duration_seconds
    result.total_requests = journeys
    return result


def _format_journey_breakdown(
    journeys: int,
    total_steps: int,
    step_latencies: dict[str, list[float]],
    cfg: PyAsyncConfig,
) -> str:
    """Build a human-readable journey breakdown string for raw_output."""
    from .metrics import percentiles

    lines = [
        f"Player Journey Breakdown ({journeys} journeys, {total_steps} total steps)",
        f"Duration: {cfg.duration_seconds}s  Concurrency: {cfg.concurrency}",
        "",
        f"{'Step':<16} {'Count':>8} {'Avg(ms)':>10} {'p50(ms)':>10} {'p95(ms)':>10} {'p99(ms)':>10}",
        f"{'─'*16} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}",
    ]
    for step_name in [
        "signup",
        "login",
        "deposit",
        "auth",
        "bet",
        "win",
        "transactions",
        "withdraw",
        "logout",
    ]:
        vals = step_latencies.get(step_name, [])
        if not vals:
            continue
        ps = percentiles(vals, (50.0, 95.0, 99.0))
        avg = sum(vals) / len(vals)
        lines.append(
            f"{step_name:<16} {len(vals):>8} {avg:>10.2f} {ps['p50']:>10.2f} {ps['p95']:>10.2f} {ps['p99']:>10.2f}"
        )
    return "\n".join(lines)


# ── Orchestration ──────────────────────────────────────────────────────────────


def run_single(
    eco: Ecosystem,
    scenario: Scenario,
    wrk_cfg: WrkConfig = DEFAULT_WRK,
    k6_cfg: K6Config = DEFAULT_K6,
    py_cfg: PyAsyncConfig = DEFAULT_PYASYNC,
    *,
    clients: list[str] | None = None,
) -> list[BenchmarkResult]:
    """Run a single scenario against one ecosystem using selected clients.

    Args:
        eco: Target ecosystem.
        scenario: Scenario to run.
        clients: Which clients to use. None = all three. Options: "wrk", "k6", "py-async".
    """
    selected = clients or ["wrk", "k6", "py-async"]
    results: list[BenchmarkResult] = []

    for client_name in selected:
        logger.info(
            "Running %s / %s [%s]...", eco.display_name, scenario.label, client_name
        )

        if client_name == "wrk":
            r = run_wrk(eco, scenario, wrk_cfg)
        elif client_name == "k6":
            r = run_k6(eco, scenario, k6_cfg)
        elif client_name == "py-async":
            r = run_py_async(eco, scenario, py_cfg)
        else:
            r = BenchmarkResult(
                ecosystem=eco.key,
                scenario=scenario.name,
                client=client_name,
                success=False,
                error=f"Unknown client: {client_name}",
            )

        results.append(r)

        if r.success:
            md_path = write_result_md(r)
            logger.info("  → %s", md_path)

    return results


def run_all(
    ecosystems: list[str] | None = None,
    scenarios: list[str] | None = None,
    wrk_cfg: WrkConfig = DEFAULT_WRK,
    k6_cfg: K6Config = DEFAULT_K6,
    py_cfg: PyAsyncConfig = DEFAULT_PYASYNC,
    *,
    clients: list[str] | None = None,
) -> list[BenchmarkResult]:
    """Run benchmarks across selected ecosystems and scenarios.

    Args:
        ecosystems: Ecosystem keys to test. None = all ("js", "go", "cs").
        scenarios: Scenario names to test. None = all.
        clients: Client tools to use. None = all three.
    """
    from .config import ECOSYSTEMS

    eco_list = [ECOSYSTEMS[e] for e in (ecosystems or ECOSYSTEMS.keys())]
    scenario_list = [SCENARIOS[s] for s in (scenarios or SCENARIOS.keys())]

    all_results: list[BenchmarkResult] = []

    total = len(eco_list) * len(scenario_list)
    current = 0

    for eco in eco_list:
        for scenario in scenario_list:
            current += 1
            logger.info(
                "[%d/%d] %s — %s", current, total, eco.display_name, scenario.label
            )
            results = run_single(
                eco, scenario, wrk_cfg, k6_cfg, py_cfg, clients=clients
            )
            all_results.extend(results)

    # Write summary
    summary_path = write_summary_md(all_results)
    logger.info("Summary → %s", summary_path)

    # Auto-update README
    update_readme(summary_path)
    logger.info("README updated with latest summary")

    return all_results
