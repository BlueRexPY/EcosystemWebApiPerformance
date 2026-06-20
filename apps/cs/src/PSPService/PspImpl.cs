using CasinoApi.Ledger;
using CasinoApi.Psp;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Grpc.Net.Client;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.PSPService;

/// <summary>
/// PSP service — handles deposit and withdrawal callbacks.
/// Settles directly into Ledger. Idempotency via Redis + outbox.
/// </summary>
public sealed partial class PspImpl : Psp.PSPService.PSPServiceBase
{
    private readonly PspDbContext _database;
    private readonly RedisStore _redis;
    private readonly ILogger<PspImpl> _logger;
    private readonly LedgerService.LedgerServiceClient _ledger;

    public PspImpl(PspDbContext database, RedisStore redis, ILogger<PspImpl> logger)
    {
        _database = database;
        _redis = redis;
        _logger = logger;
        GrpcChannel channel = GrpcChannel.ForAddress(ServiceEndpoints.Ledger);
        _ledger = new LedgerService.LedgerServiceClient(channel);
    }
}
