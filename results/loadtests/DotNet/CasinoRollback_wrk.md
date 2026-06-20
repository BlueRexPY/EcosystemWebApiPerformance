# .NET 10 — casino_rollback Benchmark

**Tested**: 2026-06-20 03:18:55 UTC
**Client**: wrk
**Duration**: 20.0s

> **Warning**: 10271 errors occurred during this test.

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 31,394 |
| Requests/sec | 1,568.10 |
| Duration | 20.02s |
| Errors | 10271 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 95.80ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 488.77ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 262.9MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 6.25% |
| PIDs | 113 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/casino/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    95.80ms   92.56ms 488.77ms   86.47%
    Req/Sec   788.66    640.46     2.57k    67.09%
  31394 requests in 20.02s, 5.16MB read
  Non-2xx or 3xx responses: 10271
Requests/sec:   1568.10
Transfer/sec:    263.74KB
```
