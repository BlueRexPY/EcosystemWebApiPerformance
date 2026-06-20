# .NET 10 — psp_deposit Benchmark

**Tested**: 2026-06-20 03:19:17 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 636,751 |
| Requests/sec | 31,817.42 |
| Duration | 20.01s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 4.39ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 38.01ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 262.7MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.07% |
| PIDs | 130 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/psp/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.39ms    4.02ms  38.01ms   91.08%
    Req/Sec    16.00k     3.01k   23.01k    62.00%
  636751 requests in 20.01s, 153.03MB read
Requests/sec:  31817.42
Transfer/sec:      7.65MB
```
