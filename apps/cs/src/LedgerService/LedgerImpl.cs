using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.LedgerService;

/// <summary>
/// Ledger — the critical path. Handles reserve/commit/settle/rollback
/// with optimistic locking (version column) + Redis write lock on reserve.
/// </summary>
public sealed partial class LedgerImpl : Ledger.LedgerService.LedgerServiceBase
{
    private readonly LedgerDbContext _database;
    private readonly RedisStore _redis;
    private readonly ILogger<LedgerImpl> _logger;

    public LedgerImpl(LedgerDbContext database, RedisStore redis, ILogger<LedgerImpl> logger)
    {
        _database = database;
        _redis = redis;
        _logger = logger;
    }

    public override async Task<GetBalanceReply> GetBalance(
        GetBalanceRequest request,
        ServerCallContext context
    )
    {
        Guid playerId = Guid.Parse(request.PlayerId);
        Wallet? wallet = await _database
            .Wallets.AsNoTracking()
            .FirstOrDefaultAsync(w => w.PlayerId == playerId);

        if (wallet is not null)
            return new GetBalanceReply
            {
                Balance = wallet.Balance,
                Reserved = wallet.Reserved,
                Version = wallet.Version
            };

        return new GetBalanceReply
        {
            Balance = NumericDefaults.InitialBalance,
            Reserved = NumericDefaults.InitialReserved,
            Version = 0
        };
    }

    private static string Serialize<T>(T value) => System.Text.Json.JsonSerializer.Serialize(value);

    private static T Deserialize<T>(string json) =>
        System.Text.Json.JsonSerializer.Deserialize<T>(json)!;
}
