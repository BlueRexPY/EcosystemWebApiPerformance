using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace CasinoApi.Shared;

public static class Db
{
    public static IServiceCollection AddPlayerDatabase(
        this IServiceCollection services,
        string connectionString
    ) => services.AddDbContextPool<PlayerDbContext>(options => options.UseNpgsql(connectionString));

    public static IServiceCollection AddLedgerDatabase(
        this IServiceCollection services,
        string connectionString
    ) => services.AddDbContextPool<LedgerDbContext>(options => options.UseNpgsql(connectionString));

    public static IServiceCollection AddCasinoDatabase(
        this IServiceCollection services,
        string connectionString
    ) => services.AddDbContextPool<CasinoDbContext>(options => options.UseNpgsql(connectionString));

    public static IServiceCollection AddPspDatabase(
        this IServiceCollection services,
        string connectionString
    ) => services.AddDbContextPool<PspDbContext>(options => options.UseNpgsql(connectionString));
}
