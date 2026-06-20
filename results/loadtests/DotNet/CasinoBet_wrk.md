# .NET 10 — casino_bet Benchmark

**Tested**: 2026-06-20 03:18:12 UTC
**Client**: wrk
**Duration**: 20.0s

## Throughput

| Metric | Value |
| --- | --- |
| Total Requests | 852,527 |
| Requests/sec | 42,614.27 |
| Duration | 20.01s |
| Errors | 0 |

## Latency (ms)

| Percentile | Latency |
| --- | --- |
| min | 0.00ms |
| avg | 3.49ms |
| stdev | 0.00ms |
| p50 | 0.00ms |
| p75 | 0.00ms |
| p90 | 0.00ms |
| p95 | 0.00ms |
| p99 | 0.00ms |
| p99.9 | 0.00ms |
| max | 123.82ms |

## Status Codes

| Code | Count |
| --- | --- |
| — | — |

## Resource Usage

| Metric | Value |
| --- | --- |
| Memory Usage | 266.8MiB |
| Memory Limit | 62.53GiB |
| Memory % | 0.42% |
| CPU % | 0.43% |
| PIDs | 128 |

## Raw Output

```
Running 20s test @ http://127.0.0.1:3002/casino/callback
  2 threads and 120 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.49ms    5.81ms 123.82ms   95.21%
    Req/Sec    21.42k     2.10k   25.79k    82.75%
  852527 requests in 20.01s, 212.20MB read
Requests/sec:  42614.27
Transfer/sec:     10.61MB
```
