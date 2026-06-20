using StackExchange.Redis;

namespace CasinoApi.Shared;

public sealed class RedisLock : IAsyncDisposable
{
    private readonly IDatabase _database;
    private readonly string _key;
    private readonly string _token;

    private static readonly string ReleaseScript =
        @"
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
        else
            return 0
        end";

    public RedisLock(IDatabase database, string key, string token)
    {
        _database = database;
        _key = key;
        _token = token;
    }

    public async ValueTask DisposeAsync()
    {
        await _database.ScriptEvaluateAsync(
            ReleaseScript,
            new RedisKey[] { _key },
            new RedisValue[] { _token }
        );
    }
}
