using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.LedgerService;

public sealed partial class LedgerImpl
{
    public override async Task<ListTransactionsReply> ListTransactions(
        ListTransactionsRequest request,
        ServerCallContext context
    )
    {
        Guid playerId = Guid.Parse(request.PlayerId);
        int limit = request.Limit > 0 ? request.Limit : GameDefaults.DefaultTransactionLimit;

        List<TransactionItem> items = await _database
            .Transactions.AsNoTracking()
            .Where(t => t.PlayerId == playerId)
            .OrderByDescending(t => t.CreatedAt)
            .Take(limit)
            .Select(t => new TransactionItem
            {
                Id = t.Id.ToString(),
                Type = t.Type,
                AmountCents = t.AmountCents,
                CreatedAt = t.CreatedAt.ToString("o")
            })
            .ToListAsync();

        ListTransactionsReply reply = new ListTransactionsReply();
        reply.Items.AddRange(items);
        return reply;
    }

    public override async Task<EnsureWalletReply> EnsureWallet(
        EnsureWalletRequest request,
        ServerCallContext context
    )
    {
        Guid playerId = Guid.Parse(request.PlayerId);
        bool exists = await _database.Wallets.AnyAsync(w => w.PlayerId == playerId);
        if (!exists)
        {
            _database.Wallets.Add(Wallet.CreateNew(playerId));
            await _database.SaveChangesAsync();
        }
        return new EnsureWalletReply { Success = true };
    }
}
