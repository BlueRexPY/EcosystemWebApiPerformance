# .NET 10 — player_me Benchmark

**Tested**: 2026-06-20 03:20:43 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 383,905 |
| Requests/sec | 19,168.00 |
| Duration | 20.03s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 6.51ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 55.61ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 265MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.06% |
| PIDs | 125 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/graphql
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.51ms    3.87ms  55.61ms   86.85%
    Req/Sec     9.64k     1.09k   11.96k    71.00%
  383905 requests in 20.03s, 189.28MB read
Requests/sec:  19168.00
Transfer/sec:      9.45MB
```
