# .NET 10 — mixed_casino Benchmark

**Tested**: 2026-06-20 03:38:03 UTC
**Client**: wrk
**Duration**: 20.0s

> **Warning**: 5436 errors occurred during this test.

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 430,648 |
| Requests/sec | 21,504.98 |
| Duration | 20.03s |
| Errors | 5436 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 20.22ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 254.58ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 264.9MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 3.09% |
| PIDs | 132 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/casino/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    20.22ms   39.25ms 254.58ms   87.99%
    Req/Sec    10.84k     4.17k   19.46k    60.30%
  430648 requests in 20.03s, 105.51MB read
  Non-2xx or 3xx responses: 5436
Requests/sec:  21504.98
Transfer/sec:      5.27MB
```
