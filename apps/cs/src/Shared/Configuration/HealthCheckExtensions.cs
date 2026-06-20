using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using StackExchange.Redis;

namespace CasinoApi.Shared;

public static class HealthCheckExtensions
{
    public static IHealthChecksBuilder AddRedisHealthCheck(this IHealthChecksBuilder builder)
    {
        return builder.AddCheck<RedisHealthCheck>("redis", tags: ["ready"]);
    }
}

internal sealed class RedisHealthCheck(RedisStore redis) : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default
    )
    {
        await redis.Db.PingAsync();
        return HealthCheckResult.Healthy();
    }
}
