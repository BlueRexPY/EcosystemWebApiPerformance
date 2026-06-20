using CasinoApi.Casino;
using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using Grpc.Core;
using Grpc.Net.Client;

namespace CasinoApi.CasinoService;

/// <summary>
/// Casino service — handles bet/win/rollback from providers.
/// Calls LedgerService for reserve/commit/settle and PlayerService for validation.
/// Idempotency via Redis + durable outbox table.
/// </summary>
public sealed partial class CasinoImpl : Casino.CasinoService.CasinoServiceBase
{
    private readonly CasinoDbContext _database;
    private readonly RedisStore _redis;
    private readonly ILogger<CasinoImpl> _logger;
    private readonly LedgerService.LedgerServiceClient _ledger;
    private readonly PlayerService.PlayerServiceClient _player;

    public CasinoImpl(CasinoDbContext database, RedisStore redis, ILogger<CasinoImpl> logger)
    {
        _database = database;
        _redis = redis;
        _logger = logger;
        GrpcChannel ledgerChannel = GrpcChannel.ForAddress(ServiceEndpoints.Ledger);
        _ledger = new LedgerService.LedgerServiceClient(ledgerChannel);
        GrpcChannel playerChannel = GrpcChannel.ForAddress(ServiceEndpoints.Player);
        _player = new PlayerService.PlayerServiceClient(playerChannel);
    }
}
