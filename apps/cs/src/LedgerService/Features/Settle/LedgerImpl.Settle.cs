using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.LedgerService;

public sealed partial class LedgerImpl
{
    public override async Task<SettleReply> Settle(SettleRequest request, ServerCallContext context)
    {
        string idempotencyKey = CacheKeys.IdempotencyLedger(request.IdempotencyKey);

        string? cached = await _redis.GetIdempotencyResult(idempotencyKey);

        if (cached is not null)
            return Deserialize<SettleReply>(cached);

        Guid playerId = Guid.Parse(request.PlayerId);

        await using Microsoft.EntityFrameworkCore.Storage.IDbContextTransaction databaseTransaction =
            await _database.Database.BeginTransactionAsync();

        Wallet? wallet = await _database.Wallets.FirstOrDefaultAsync(w => w.PlayerId == playerId);

        bool isNewWallet = wallet is null;

        wallet ??= Wallet.CreateNew(playerId);
        wallet.Credit(request.Amount);

        if (isNewWallet)
            _database.Wallets.Add(wallet);

        Transaction transaction = Transaction.Settle(
            playerId,
            request.Amount,
            request.IdempotencyKey
        );

        _database.Transactions.Add(transaction);

        await _database.SaveChangesAsync();
        await databaseTransaction.CommitAsync();

        SettleReply result = new() { Success = true, TransactionId = transaction.Id.ToString() };

        await _redis.Db.StringSetAsync(
            idempotencyKey,
            Serialize(result),
            CasinoConfig.IdempotencyTimeToLiveCasino
        );

        await _redis.Invalidate(CacheKeys.Balance(request.PlayerId));

        return result;
    }
}
