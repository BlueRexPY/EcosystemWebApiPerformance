# .NET 10 — casino_auth Benchmark

**Tested**: 2026-06-20 03:17:51 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 228,876 |
| Requests/sec | 11,428.51 |
| Duration | 20.03s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 10.68ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 78.98ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 266.1MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.42% |
| CPU % | 92.52% |
| PIDs | 129 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/casino/authenticate
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    10.68ms    4.82ms  78.98ms   88.41%
    Req/Sec     5.75k   658.07     6.97k    79.75%
  228876 requests in 20.03s, 62.64MB read
Requests/sec:  11428.51
Transfer/sec:      3.13MB
```
