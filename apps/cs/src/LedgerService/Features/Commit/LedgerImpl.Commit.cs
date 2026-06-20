using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.LedgerService;

public sealed partial class LedgerImpl
{
    public override async Task<CommitReply> Commit(CommitRequest request, ServerCallContext context)
    {
        Guid transactionId = Guid.Parse(request.TransactionId);

        Transaction? reserveTransaction = await _database.Transactions.FirstOrDefaultAsync(t =>
            t.Id == transactionId && t.Type == TransactionTypes.Reserve
        );

        if (reserveTransaction is null)
            return new CommitReply { Success = false, Error = ErrorCodes.TxNotFound };

        await using Microsoft.EntityFrameworkCore.Storage.IDbContextTransaction databaseTransaction =
            await _database.Database.BeginTransactionAsync();

        Wallet? wallet = await _database.Wallets.FirstOrDefaultAsync(w =>
            w.PlayerId == reserveTransaction.PlayerId
        );

        if (wallet is null || wallet.Reserved < reserveTransaction.AmountCents)
        {
            await databaseTransaction.RollbackAsync();
            return new CommitReply { Success = false, Error = ErrorCodes.CommitFailed };
        }

        wallet.Debit(reserveTransaction.AmountCents);
        wallet.Release(reserveTransaction.AmountCents);

        // version handled by domain methods
        Transaction commitTransaction =
            new()
            {
                Id = Guid.NewGuid(),
                PlayerId = reserveTransaction.PlayerId,
                Type = TransactionTypes.Commit,
                AmountCents = reserveTransaction.AmountCents
            };
        _database.Transactions.Add(commitTransaction);

        await _database.SaveChangesAsync();
        await databaseTransaction.CommitAsync();
        await _redis.Invalidate(CacheKeys.Balance(reserveTransaction.PlayerId));

        return new CommitReply
        {
            Success = true,
            NewBalance = NumericDefaults.InitialBalance,
            NewReserved = NumericDefaults.InitialReserved
        };
    }
}
