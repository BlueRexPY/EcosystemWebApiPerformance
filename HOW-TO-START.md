# How to Start — Ecosystem Web API Performance Benchmark

## Prerequisites

| Tool               | Min Version | Check                      |
| ------------------ | ----------- | -------------------------- |
| Docker + Compose   | 24+         | `docker compose version`   |
| Bun                | 1.1+        | `bun --version`            |
| Go                 | 1.22+       | `go version`               |
| .NET SDK           | 9.0+        | `dotnet --version`         |
| kubectl (optional) | 1.29+       | `kubectl version --client` |

## 1. Infrastructure Layer

```bash
# Start PostgreSQL, Redis, NATS, Prometheus
docker compose up -d

# Confirm all four are healthy
docker compose ps

# Verify 100,000 players seeded
docker exec -it casino_postgres psql -U engine_admin -d casino_db -c "SELECT COUNT(*) FROM wallets;"
# Expected: 100000
```

## 2. Run the Stacks

### Bun + Elysia (TypeScript)

```bash
cd apps/js
bun install
bun run dev
# Listening on :3000
```

### Go + Fiber

```bash
cd apps/go
go run .
# Listening on :3001
```

### .NET 9

```bash
cd apps/cs
dotnet run
# Listening on :3002
```

## 3. Run the Benchmark

```bash
cd clients
# TBD — load-generation harness details coming soon
```

## 4. Kubernetes Deployment (Optional)

```bash
# Apply infra manifests (Redis, NATS, namespace)
kubectl apply -f k8s/infra.yaml

# Deploy each stack (manifests TBD)
# kubectl apply -f apps/go/k8s/
# kubectl apply -f apps/js/k8s/
# kubectl apply -f apps/cs/k8s/
```

## Endpoints

Each stack exposes the same REST contract:

| Method | Path                       | Description                  |
| ------ | -------------------------- | ---------------------------- |
| `POST` | `/wallet/:playerId/bet`    | Place a bet (deduct balance) |
| `POST` | `/wallet/:playerId/win`    | Record a win (add balance)   |
| `GET`  | `/wallet/:playerId`        | Read current balance         |
| `GET`  | `/wallet/:playerId/ledger` | Fetch transaction history    |
| `GET`  | `/health`                  | Liveness probe               |
| `GET`  | `/metrics`                 | Prometheus scrape target     |

## Useful Commands

```bash
# Tail NATS monitoring
curl http://localhost:8222/varz

# Check Redis hit/miss ratio
docker exec -it casino_redis redis-cli INFO stats | grep keyspace

# Postgres active connections
docker exec -it casino_postgres psql -U engine_admin -d casino_db -c "SELECT count(*) FROM pg_stat_activity;"

# Prometheus UI
open http://localhost:9090
```
