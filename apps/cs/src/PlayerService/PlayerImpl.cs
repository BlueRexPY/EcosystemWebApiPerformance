using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Grpc.Net.Client;

namespace CasinoApi.PlayerService;

public sealed partial class PlayerImpl : Player.PlayerService.PlayerServiceBase
{
    private readonly PlayerDbContext _database;
    private readonly RedisStore _redis;
    private readonly LedgerService.LedgerServiceClient _ledger;

    public PlayerImpl(PlayerDbContext database, RedisStore redis)
    {
        _database = database;
        _redis = redis;
        GrpcChannel ledgerChannel = GrpcChannel.ForAddress(ServiceEndpoints.Ledger);
        _ledger = new LedgerService.LedgerServiceClient(ledgerChannel);
    }
}
