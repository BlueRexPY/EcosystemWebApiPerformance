# .NET 10 — mixed_full Benchmark

**Tested**: 2026-06-20 03:38:25 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 194,919 |
| Requests/sec | 9,733.92 |
| Duration | 20.02s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 13.44ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 196.65ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 264.7MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.07% |
| PIDs | 129 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/casino/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    13.44ms   12.05ms 196.65ms   94.08%
    Req/Sec     4.91k     1.01k    6.79k    68.09%
  194919 requests in 20.02s, 53.35MB read
Requests/sec:   9733.92
Transfer/sec:      2.66MB
```
