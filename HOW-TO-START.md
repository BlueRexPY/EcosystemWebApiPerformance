# How to Start — Casino Microservices Benchmark

## Prerequisites

| Tool             | Min Version | Check                    |
| ---------------- | ----------- | ------------------------ |
| Docker + Compose | 24+         | `docker compose version` |
| .NET SDK         | 10.0+       | `dotnet --version`       |
| Python           | 3.9+        | `python3 --version`      |
| wrk              | 4.1+        | `wrk --version`          |

## 1. Start Everything

```bash
cd /home/admin/Projects/Benchmarks/EcosystemWebApiPerfromance

# Start all 12 containers: 4 PostgreSQL, Redis, Prometheus, 5 microservices
docker compose up -d --build

# Wait for healthy (~30s for DB seeding of 100K rows)
watch docker compose ps

# Verify seed data
docker exec casino_pg_player psql -U engine_admin -d player_db -c "SELECT COUNT(*) FROM players;"
# → 100000

docker exec casino_pg_ledger psql -U engine_admin -d ledger_db -c "SELECT COUNT(*) FROM wallets;"
# → 100000
```

## 2. Smoke Test

```bash
# Health check
curl http://localhost:3002/health
# → Healthy

# GraphQL login
curl -s -X POST http://localhost:3002/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { login(username: \"player_000001\", password: \"test\") { token player { id username } } }"}'

# REST authenticate
curl -s -X POST http://localhost:3002/casino/authenticate \
  -H "Content-Type: application/json" \
  -d '{"token":"session-player-00001","gameId":"slot-mega-7"}'

# REST bet
curl -s -X POST http://localhost:3002/casino/callback \
  -H "Content-Type: application/json" \
  -d '{"type":"bet","amountCents":1000,"transactionId":"tx-001","roundId":"round-001","token":"session-player-00001","gameId":"slot-mega-7"}'
```

## 3. Run Benchmarks

```bash
# List available scenarios
python3 -m clients.loadtest list

# Quick single test (5s)
python3 -m clients.loadtest run --ecosystem cs --scenario casino_bet --client wrk --duration 5

# Full .NET 10 suite (12 scenarios, 20s each)
python3 -m clients.loadtest run --ecosystem cs --client wrk

# Compare all ecosystems
python3 -m clients.loadtest run --client wrk --ecosystem cs --ecosystem go --ecosystem js
```

Results auto-saved to `results/loadtests/Summary.md` and auto-injected into `README.md`.

## Service Map

| Service       | Port | DB Port | DB Name   | Health    |
| ------------- | ---- | ------- | --------- | --------- |
| Gateway       | 3002 | —       | —         | `/health` |
| PlayerService | 5001 | 5433    | player_db | gRPC      |
| LedgerService | 5002 | 5434    | ledger_db | gRPC      |
| CasinoService | 5003 | 5435    | casino_db | gRPC      |
| PSPService    | 5004 | 5436    | psp_db    | gRPC      |
| Redis         | 6379 | —       | —         | `PING`    |

## Useful Commands

```bash
# Check all container logs
docker compose logs -f --tail=20

# Check a specific service
docker logs casino_gateway --tail=30

# PostgreSQL — active connections
docker exec casino_pg_ledger psql -U engine_admin -d ledger_db -c "SELECT count(*) FROM pg_stat_activity;"

# Redis — keyspace stats
docker exec casino_redis redis-cli INFO keyspace

# Rebuild after code changes
docker compose build --no-cache && docker compose up -d --force-recreate
```

## Seed Data

- **100,000 players** (`player_000001` … `player_100000`) in `player_db`
- **100,000 wallets** with matching UUIDs, $100,000 each in `ledger_db`
- Casino and PSP databases schema-only (filled at runtime)
- Deterministic UUIDs via `uuid_generate_v5` — same player has same ID across DBs
