# .NET 10 — casino_win Benchmark

**Tested**: 2026-06-20 03:18:34 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 820,508 |
| Requests/sec | 40,995.05 |
| Duration | 20.01s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 3.67ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 108.25ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 267.5MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.42% |
| CPU % | 92.94% |
| PIDs | 128 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/casino/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.67ms    5.99ms 108.25ms   95.30%
    Req/Sec    20.60k     2.81k   27.35k    77.50%
  820508 requests in 20.01s, 204.23MB read
Requests/sec:  40995.05
Transfer/sec:     10.20MB
```
