using CasinoApi.Casino;
using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;

namespace CasinoApi.CasinoService;

public sealed partial class CasinoImpl
{
    public override async Task<BetReply> Bet(BetRequest request, ServerCallContext context)
    {
        string idempotencyKey = CacheKeys.IdempotencyCasino(request.ProviderTransactionId);
        string? cached = await _redis.GetIdempotencyResult(idempotencyKey);
        if (cached is not null)
            return System.Text.Json.JsonSerializer.Deserialize<BetReply>(cached)!;

        string? outboxResult = await CheckOutbox(request.ProviderTransactionId);
        if (outboxResult is not null)
        {
            await _redis.Db.StringSetAsync(
                idempotencyKey,
                outboxResult,
                CasinoConfig.IdempotencyTimeToLiveCasino
            );
            return System.Text.Json.JsonSerializer.Deserialize<BetReply>(outboxResult)!;
        }

        string? playerId = await ResolveSessionPlayer(request.SessionToken);
        if (playerId is null)
            return new BetReply { Success = false, Error = ErrorCodes.InvalidSession };

        GetPlayerReply playerResult = await _player.GetPlayerAsync(
            new GetPlayerRequest { PlayerId = playerId }
        );
        if (!playerResult.Found)
            return new BetReply { Success = false, Error = ErrorCodes.PlayerNotFound };

        ReserveReply reserveResult = await _ledger.ReserveAsync(
            new ReserveRequest
            {
                PlayerId = playerId,
                Amount = request.Amount,
                IdempotencyKey = IdempotencyKeys.CasinoBet(request.ProviderTransactionId)
            }
        );
        if (!reserveResult.Success)
            return new BetReply { Success = false, Error = reserveResult.Error };

        CommitReply commitResult = await _ledger.CommitAsync(
            new CommitRequest { TransactionId = reserveResult.TransactionId }
        );
        if (!commitResult.Success)
        {
            await _ledger.RollbackAsync(
                new RollbackRequest { TransactionId = reserveResult.TransactionId }
            );
            return new BetReply { Success = false, Error = ErrorCodes.CommitFailed };
        }

        Guid playerGuid = Guid.Parse(playerId);
        Guid roundTransactionId = Guid.NewGuid();

        RoundTransaction roundTransaction = new RoundTransaction
        {
            Id = roundTransactionId,
            PlayerId = playerGuid,
            ProviderTransactionId = request.ProviderTransactionId,
            Type = TransactionTypes.Bet,
            AmountCents = request.Amount,
            GameId = request.GameId,
            RoundId = request.RoundId,
            LedgerTransactionId = Guid.Parse(reserveResult.TransactionId)
        };
        _database.RoundTransactions.Add(roundTransaction);

        BetReply result = new BetReply
        {
            Success = true,
            RoundTransactionId = roundTransactionId.ToString()
        };
        string resultJson = System.Text.Json.JsonSerializer.Serialize(result);

        CasinoOutbox outbox = new CasinoOutbox
        {
            ProviderTransactionId = request.ProviderTransactionId,
            ResultJson = resultJson
        };
        _database.CasinoOutbox.Add(outbox);

        await _database.SaveChangesAsync();
        await _redis.Db.StringSetAsync(
            idempotencyKey,
            resultJson,
            CasinoConfig.IdempotencyTimeToLiveCasino
        );

        return result;
    }
}
