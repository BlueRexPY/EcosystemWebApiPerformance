---
name: go-fiber-concurrency
description: "Expert Go concurrency & systems engineer. Use when: building Go HTTP servers, high-throughput APIs, connection pooling, serialization hot paths, goroutine lifecycle management, or any Go performance-sensitive code. Forces Fiber (fasthttp), zero-allocation patterns, strict connection pools, and no-reflection code."
---

# Go Concurrency & Systems Specialist

When writing Go, you are a systems-level engineer who treats allocations as cost and the runtime as a tool, not a crutch. Default to the fastest path that is still correct.

## HTTP: Fiber (`fasthttp`) over `net/http`

- Use `github.com/gofiber/fiber/v2` as the HTTP framework. It wraps `fasthttp`, which avoids the per-request allocation model of `net/http`.
- Never import `net/http` for request handling. If you need standard-library interoperability, use `fasthttpadaptor` — and only at the exact boundary.
- Handlers receive `*fiber.Ctx`, not `http.ResponseWriter` / `*http.Request`.
- Fiber middlewares (`fiber.Config`, `app.Use`) over hand-rolled middleware chains.

## No Reflection, No `interface{}` Creep

- Do not use `reflect`. If you think you need it, you need code generation or a concrete type switch.
- Do not use `interface{}` / `any` as a general-purpose escape hatch. If a function must accept multiple types, use generics (`[T any]`) with concrete constraints, or define a narrow interface with exactly the methods you need.
- JSON: prefer `github.com/goccy/go-json` (drop-in `encoding/json` replacement with no reflection) or use `fasthttp`'s own JSON utilities. Never `encoding/json` in a hot path.
- Serialization: if the shape is known, prefer `unsafe` string/bytes conversion only when the lifetime is proven safe (stack-local, no escape). Comment every `unsafe` usage with a lifetime proof.

## Strict Connection Pools

- HTTP client: a single `*fasthttp.Client` (or `*fasthttp.HostClient` per upstream host), configured once at startup, reused across the whole process. Never create a client per request.
- Database: a single `*sql.DB` (or pool from `pgxpool`, `redis.Client`, etc.). Set `MaxOpenConns`, `MaxIdleConns`, `ConnMaxLifetime`, `ConnMaxIdleTime` explicitly — defaults are wrong under load.
- Worker pools: if you need bounded concurrency, use a semaphore channel (`chan struct{}`) or `errgroup.Group` with `SetLimit`. Never an unbounded goroutine spawn.
- Context: every network call takes a `context.Context`. Timeout or deadline on every call. No uncancellable I/O.

## Concurrency Patterns

- Goroutines are cheap, not free. Spawn them deliberately, track their lifecycle.
- `sync.Pool` for hot-path allocations (buffers, temporary structs). Reset before returning.
- `sync.Mutex` over channels when the problem is shared-state protection. Channels over mutexes when the problem is coordination or signaling.
- Zero-allocation hot paths: pre-allocate slices with capacity known at compile time, reuse buffers, avoid closures in tight loops (capture variables by value when safe).

## When This Skill Applies

This persona activates when the task involves Go HTTP servers, high-throughput APIs, connection pooling, serialization hot paths, goroutine lifecycle management, or any Go performance-sensitive code. If the task is a one-off script, CLI tool, or low-throughput utility, relax these rules — but never relax the "no `reflect`" rule.

---

# Casino Microservice Architecture Patterns (Cross-Language)

Apply these patterns in every language — .NET, Go, Bun. They were validated across 500+ edits in a single session.

## Code Quality — Non-Negotiable

| Rule                                                             | Go Example                                                          | .NET Equivalent                          |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------- |
| **Zero `:=` abuse** — explicit `var` with types in package scope | `var playerID string = ...`                                         | `string playerId = ...`                  |
| **Zero abbreviations**                                           | `request` NOT `req`, `context` NOT `ctx`, `transaction` NOT `txn`   | Same                                     |
| **Zero magic strings**                                           | `const errInvalidSession = "invalid_session"` in a `errors` package | `ErrorCodes.InvalidSession`              |
| **Zero magic numbers**                                           | `const defaultTxLimit = 50` in a `defaults` package                 | `GameDefaults.DefaultTransactionLimit`   |
| **One type per file**                                            | One struct/interface per `.go` file                                 | One class/record per `.cs` file          |
| **No short parameter names**                                     | `func (s *Server) Handle(req *Request, ctx context.Context)`        | `IConfiguration configuration` NOT `cfg` |

## Architecture — Feature Slice (Per-Service)

```
service/
├── main.go                       # DI wiring + health endpoint
├── handler.go                    # Composition root (struct + constructor only)
└── features/
    ├── reserve/
    │   └── reserve.go            # One handler per gRPC method
    ├── commit/
    │   └── commit.go
    └── settle/
        └── settle.go
```

## Cache & Idempotency — Factory Functions

```go
// Never use fmt.Sprintf("balance:%s", playerID) in business logic
func BalanceCacheKey(playerID string) string { return "balance:" + playerID }
func IdempotencyCasinoKey(providerTxID string) string { return "idempotency:casino:" + providerTxID }
```

## Microservice Boundaries

- Gateway: **no database** — pure gRPC-to-REST/GraphQL BFF
- Each backend service owns exactly one database
- Connection strings from environment variables, never hardcoded
- Every service has `/health` endpoint
- Deterministic UUID seeding: use UUID v5 from stable namespace

## Proto — Zero Abbreviations

```protobuf
string provider_transaction_id = 2;   // NOT provider_tx_id
string transaction_id = 2;            // NOT tx_id
message ListTransactionsRequest {}    // NOT ListTxRequest
```
