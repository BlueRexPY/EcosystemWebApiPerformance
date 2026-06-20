using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.LedgerService;

public sealed partial class LedgerImpl
{
    public override async Task<RollbackReply> Rollback(
        RollbackRequest request,
        ServerCallContext context
    )
    {
        Guid transactionId = Guid.Parse(request.TransactionId);

        Transaction? reserveTransaction = await _database.Transactions.FirstOrDefaultAsync(t =>
            t.Id == transactionId && t.Type == TransactionTypes.Reserve
        );

        if (reserveTransaction is null)
            return new RollbackReply { Success = false, Error = ErrorCodes.TxNotFound };

        Wallet? wallet = await _database.Wallets.FirstOrDefaultAsync(w =>
            w.PlayerId == reserveTransaction.PlayerId
        );

        if (wallet is null || wallet.Reserved < reserveTransaction.AmountCents)
            return new RollbackReply { Success = false, Error = ErrorCodes.RollbackFailed };

        wallet.Release(reserveTransaction.AmountCents);
        // version handled by domain methods

        Transaction rollbackTransaction = new Transaction
        {
            Id = Guid.NewGuid(),
            PlayerId = reserveTransaction.PlayerId,
            Type = TransactionTypes.Rollback,
            AmountCents = reserveTransaction.AmountCents
        };
        _database.Transactions.Add(rollbackTransaction);

        await _database.SaveChangesAsync();
        await _redis.Invalidate(CacheKeys.Balance(reserveTransaction.PlayerId));
        return new RollbackReply { Success = true };
    }
}
