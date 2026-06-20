# .NET 10 — player_transactions Benchmark

**Tested**: 2026-06-20 03:21:05 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 389,110 |
| Requests/sec | 19,435.46 |
| Duration | 20.02s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 6.30ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 39.45ms |

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
| CPU % | 0.05% |
| PIDs | 124 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/graphql
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.30ms    3.27ms  39.45ms   83.44%
    Req/Sec     9.77k   818.92    11.75k    69.50%
  389110 requests in 20.02s, 191.85MB read
Requests/sec:  19435.46
Transfer/sec:      9.58MB
```
