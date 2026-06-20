# .NET 10 — player_balance Benchmark

**Tested**: 2026-06-20 03:20:21 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 375,225 |
| Requests/sec | 18,743.61 |
| Duration | 20.02s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 6.65ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 42.91ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 264.4MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.04% |
| PIDs | 126 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/graphql
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.65ms    3.79ms  42.91ms   84.85%
    Req/Sec     9.42k     1.12k   11.62k    70.75%
  375225 requests in 20.02s, 185.00MB read
Requests/sec:  18743.61
Transfer/sec:      9.24MB
```
