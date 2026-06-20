using StackExchange.Redis;

namespace CasinoApi.Shared;

/// <summary>
/// Thin wrapper around StackExchange.Redis for idempotency checks,
/// read-through cache, and distributed write locks.
/// </summary>
public sealed class RedisStore
{
    private readonly ConnectionMultiplexer _redis;
    public IDatabase Db { get; }

    public RedisStore(string connectionString)
    {
        _redis = ConnectionMultiplexer.Connect(connectionString);
        Db = _redis.GetDatabase();
    }

    /// <summary>Check and set idempotency key. Returns true if key did NOT exist (first call).</summary>
    public async ValueTask<bool> TryAcquireIdempotencyKey(
        string key,
        string value,
        TimeSpan timeToLive
    )
    {
        return await Db.StringSetAsync(key, value, timeToLive, When.NotExists);
    }

    /// <summary>Get cached idempotency result. Returns null if not found.</summary>
    public async ValueTask<string?> GetIdempotencyResult(string key)
    {
        RedisValue cachedValue = await Db.StringGetAsync(key);
        return cachedValue.HasValue ? cachedValue.ToString() : null;
    }

    /// <summary>Read-through cache helper: get or set.</summary>
    public async ValueTask<string?> GetOrSet(
        string key,
        Func<Task<string?>> factory,
        TimeSpan timeToLive
    )
    {
        RedisValue cachedValue = await Db.StringGetAsync(key);
        if (cachedValue.HasValue)
            return cachedValue.ToString();

        string? value = await factory();
        if (value is not null)
            await Db.StringSetAsync(key, value, timeToLive);
        return value;
    }

    /// <summary>Invalidate a cache key immediately.</summary>
    public async ValueTask Invalidate(string key) => await Db.KeyDeleteAsync(key);

    /// <summary>Distributed write lock. Returns disposable that releases on Dispose.</summary>
    public async ValueTask<RedisLock?> AcquireLockAsync(string key, TimeSpan timeout)
    {
        string lockKey = CacheKeys.DistributedLock(key);
        string lockToken = Guid.NewGuid().ToString("N");
        bool acquired = await Db.StringSetAsync(lockKey, lockToken, timeout, When.NotExists);
        return acquired ? new RedisLock(Db, lockKey, lockToken) : null;
    }
}
