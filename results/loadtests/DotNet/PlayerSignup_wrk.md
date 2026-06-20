# .NET 10 — player_signup Benchmark

**Tested**: 2026-06-20 03:21:26 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 57,819 |
| Requests/sec | 2,886.01 |
| Duration | 20.03s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 41.64ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 176.49ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 265.5MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.06% |
| PIDs | 122 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/graphql
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    41.64ms   14.60ms 176.49ms   71.91%
    Req/Sec     1.45k   174.99     1.96k    70.25%
  57819 requests in 20.03s, 16.93MB read
Requests/sec:   2886.01
Transfer/sec:    865.24KB
```
