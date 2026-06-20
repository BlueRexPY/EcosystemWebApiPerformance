using Microsoft.Extensions.Configuration;

namespace CasinoApi.Shared;

/// <summary>Per-service config read from appsettings.json.</summary>
public static class CasinoConfig
{
    public static string PlayerDatabase(IConfiguration configuration) =>
        configuration.GetRequiredConnectionString("PlayerDb");

    public static string LedgerDatabase(IConfiguration configuration) =>
        configuration.GetRequiredConnectionString("LedgerDb");

    public static string CasinoDatabase(IConfiguration configuration) =>
        configuration.GetRequiredConnectionString("CasinoDb");

    public static string PspDatabase(IConfiguration configuration) =>
        configuration.GetRequiredConnectionString("PspDb");

    public static string RedisConnectionString(IConfiguration configuration) =>
        configuration.GetConnectionString("Redis") ?? "127.0.0.1:6379";

    public static TimeSpan CacheTimeToLiveShort => TimeSpan.FromSeconds(5);
    public static TimeSpan CacheTimeToLiveMedium => TimeSpan.FromMinutes(1);
    public static TimeSpan IdempotencyTimeToLiveCasino => TimeSpan.FromHours(24);
    public static TimeSpan IdempotencyTimeToLivePsp => TimeSpan.FromHours(48);
    public static TimeSpan LockTimeout => TimeSpan.FromSeconds(10);

    private static string GetRequiredConnectionString(
        this IConfiguration configuration,
        string name
    ) =>
        configuration.GetConnectionString(name)
        ?? throw new InvalidOperationException(
            $"ConnectionString '{name}' not found in appsettings.json"
        );
}
