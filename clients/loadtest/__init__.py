"""Casino API Load Testing Harness.

Three-client load testing for Bun/Elysia, Go/Fiber, and .NET 9 casino backends.
Measures throughput, latency percentiles (p50/p75/p90/p95/p99/p999),
RAM/CPU usage, and scaling behaviour.

Clients:
  1. wrk      — raw HTTP throughput (classic wrk)
  2. k6       — scripted scenarios with built-in percentile trends
  3. py-async — Python httpx async with in-process histogram (most detail)
"""

__version__ = "0.1.0"
