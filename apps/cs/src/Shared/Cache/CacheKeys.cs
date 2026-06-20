using System;

namespace CasinoApi.Shared;

/// <summary>Cache key factory. All Redis keys are built here.</summary>
public static class CacheKeys
{
    public static string IdempotencyCasino(string providerTransactionId) =>
        $"idempotency:casino:{providerTransactionId}";

    public static string IdempotencyLedger(string idempotencyKey) =>
        $"idempotency:ledger:{idempotencyKey}";

    public static string IdempotencyPsp(string providerReference) =>
        $"idempotency:psp:{providerReference}";

    public static string Player(string playerId) => $"player:{playerId}";

    public static string Player(Guid playerId) => Player(playerId.ToString());

    public static string Balance(string playerId) => $"balance:{playerId}";

    public static string Balance(Guid playerId) => Balance(playerId.ToString());

    public static string ReserveLock(string playerId) => $"reserve:{playerId}";

    public static string DistributedLock(string key) => $"lock:{key}";
}
