# Load Test Summary

**Generated**: 2026-06-20 03:38:53 UTC

## Results

| Ecosystem | Scenario            | Client | Req/sec   | Avg      | p50      | p95      | p99      | p99.9     | Max       | Total   | Errors | Memory   |
| --------- | ------------------- | ------ | --------- | -------- | -------- | -------- | -------- | --------- | --------- | ------- | ------ | -------- |
| .NET 10   | casino_auth         | wrk    | 11,396.46 | 10.77ms  | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 104.29ms  | 228,171 | 0      | 211.1MiB |
| .NET 10   | casino_bet          | wrk    | 42,494.25 | 3.30ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 99.44ms   | 850,248 | 0      | 213.8MiB |
| .NET 10   | casino_win          | wrk    | 42,237.15 | 3.04ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 19.78ms   | 844,988 | 0      | 221.5MiB |
| .NET 10   | casino_rollback     | wrk    | 1,641.57  | 87.59ms  | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 443.66ms  | 32,874  | 9765   | 218.5MiB |
| .NET 10   | psp_deposit         | wrk    | 36,555.93 | 3.71ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 111.40ms  | 731,495 | 0      | 209.9MiB |
| .NET 10   | psp_withdrawal      | wrk    | 39,467.91 | 3.94ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 187.73ms  | 789,799 | 0      | 210.9MiB |
| .NET 10   | player_login        | wrk    | 18,453.97 | 6.76ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 88.57ms   | 369,547 | 0      | 237.8MiB |
| .NET 10   | player_balance      | wrk    | 19,360.03 | 6.44ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 41.42ms   | 387,612 | 0      | 245.3MiB |
| .NET 10   | player_me           | wrk    | 18,845.09 | 6.59ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 44.85ms   | 377,392 | 0      | 247.4MiB |
| .NET 10   | player_transactions | wrk    | 19,168.91 | 6.37ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 39.66ms   | 383,795 | 0      | 247.6MiB |
| .NET 10   | player_signup       | wrk    | 2,958.22  | 40.59ms  | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 175.45ms  | 59,272  | 0      | 248.6MiB |
| .NET 10   | player_logout       | wrk    | 15,540.52 | 7.91ms   | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 45.96ms   | 311,259 | 0      | 251.4MiB |
| .NET 10   | mixed_casino        | wrk    | 21,504.98 | 20.22ms  | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 254.58ms  | 430,648 | 5436   | 264.9MiB |
| .NET 10   | mixed_full          | wrk    | 9,733.92  | 13.44ms  | 0.00ms   | 0.00ms   | 0.00ms   | 0.00ms    | 196.65ms  | 194,919 | 0      | 264.7MiB |
| .NET 10   | player_journey      | wrk    | 23.00     | 152.49ms | 127.24ms | 170.25ms | 209.68ms | 4262.51ms | 4630.33ms | 460     | 0      | 261.4MiB |
