using CasinoApi.Casino;
using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.CasinoService;

public sealed partial class CasinoImpl
{
    public override async Task<CasinoRollbackReply> Rollback(
        CasinoRollbackRequest request,
        ServerCallContext context
    )
    {
        RoundTransaction? roundTransaction = await _database.RoundTransactions.FirstOrDefaultAsync(
            rt => rt.ProviderTransactionId == request.ProviderTransactionId
        );

        if (roundTransaction is null)
            return new CasinoRollbackReply { Success = false, Error = ErrorCodes.RoundTxNotFound };

        string ledgerTransactionId = roundTransaction.LedgerTransactionId.ToString();
        RollbackReply rollbackResult = await _ledger.RollbackAsync(
            new RollbackRequest { TransactionId = ledgerTransactionId }
        );
        return new CasinoRollbackReply
        {
            Success = rollbackResult.Success,
            Error = rollbackResult.Error
        };
    }
}
