# .NET 10 — player_logout Benchmark

**Tested**: 2026-06-20 03:21:48 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 363,826 |
| Requests/sec | 18,167.93 |
| Duration | 20.03s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 6.78ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 34.21ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 267.9MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.42% |
| CPU % | 86.96% |
| PIDs | 126 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/graphql
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.78ms    3.63ms  34.21ms   83.61%
    Req/Sec     9.13k   779.94    11.14k    68.75%
  363826 requests in 20.03s, 179.38MB read
Requests/sec:  18167.93
Transfer/sec:      8.96MB
```
