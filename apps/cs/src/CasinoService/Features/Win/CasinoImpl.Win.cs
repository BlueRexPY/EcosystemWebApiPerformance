using CasinoApi.Casino;
using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;

namespace CasinoApi.CasinoService;

public sealed partial class CasinoImpl
{
    public override async Task<WinReply> Win(WinRequest request, ServerCallContext context)
    {
        string idempotencyKey = CacheKeys.IdempotencyCasino(request.ProviderTransactionId);
        string? cached = await _redis.GetIdempotencyResult(idempotencyKey);
        if (cached is not null)
            return System.Text.Json.JsonSerializer.Deserialize<WinReply>(cached)!;

        string? playerId = await ResolveSessionPlayer(request.SessionToken);
        if (playerId is null)
            return new WinReply { Success = false, Error = ErrorCodes.InvalidSession };

        SettleReply settleResult = await _ledger.SettleAsync(
            new SettleRequest
            {
                PlayerId = playerId,
                Amount = request.Amount,
                IdempotencyKey = IdempotencyKeys.CasinoWin(request.ProviderTransactionId)
            }
        );
        if (!settleResult.Success)
            return new WinReply { Success = false, Error = settleResult.Error };

        Guid playerGuid = Guid.Parse(playerId);
        Guid roundTransactionId = Guid.NewGuid();

        RoundTransaction roundTransaction = new RoundTransaction
        {
            Id = roundTransactionId,
            PlayerId = playerGuid,
            ProviderTransactionId = request.ProviderTransactionId,
            Type = TransactionTypes.Win,
            AmountCents = request.Amount,
            GameId = request.GameId,
            RoundId = request.RoundId,
            LedgerTransactionId = Guid.Parse(settleResult.TransactionId)
        };
        _database.RoundTransactions.Add(roundTransaction);

        await _database.SaveChangesAsync();

        WinReply result = new WinReply
        {
            Success = true,
            RoundTransactionId = roundTransactionId.ToString()
        };
        string resultJson = System.Text.Json.JsonSerializer.Serialize(result);
        await _redis.Db.StringSetAsync(
            idempotencyKey,
            resultJson,
            CasinoConfig.IdempotencyTimeToLiveCasino
        );
        return result;
    }
}
