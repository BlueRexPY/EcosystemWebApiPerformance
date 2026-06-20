# .NET 10 — player_login Benchmark

**Tested**: 2026-06-20 03:20:00 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 355,318 |
| Requests/sec | 17,740.98 |
| Duration | 20.03s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 7.28ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 72.30ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 264MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.13% |
| PIDs | 124 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/graphql
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     7.28ms    5.04ms  72.30ms   88.17%
    Req/Sec     8.91k     1.44k   11.80k    59.25%
  355318 requests in 20.03s, 175.19MB read
Requests/sec:  17740.98
Transfer/sec:      8.75MB
```
