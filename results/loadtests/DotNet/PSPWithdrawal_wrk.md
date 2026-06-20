# .NET 10 — psp_withdrawal Benchmark

**Tested**: 2026-06-20 03:19:38 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 810,717 |
| Requests/sec | 40,513.23 |
| Duration | 20.01s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 3.43ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 30.50ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 262.4MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.41% |
| CPU % | 0.06% |
| PIDs | 128 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/psp/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.43ms    3.10ms  30.50ms   90.78%
    Req/Sec    20.36k     1.90k   25.56k    68.00%
  810717 requests in 20.01s, 194.84MB read
Requests/sec:  40513.23
Transfer/sec:      9.74MB
```
