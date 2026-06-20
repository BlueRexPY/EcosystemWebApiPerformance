using CasinoApi.Ledger;
using CasinoApi.Psp;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;

namespace CasinoApi.PSPService;

public sealed partial class PspImpl
{
    public override async Task<WithdrawReply> Withdraw(
        WithdrawRequest request,
        ServerCallContext context
    )
    {
        string idempotencyKey = CacheKeys.IdempotencyPsp(request.ProviderReference);
        string? cached = await _redis.GetIdempotencyResult(idempotencyKey);

        if (cached is not null)
            return System.Text.Json.JsonSerializer.Deserialize<WithdrawReply>(cached)!;

        string? outboxResult = await CheckOutbox(request.ProviderReference);
        if (outboxResult is not null)
        {
            await _redis.Db.StringSetAsync(
                idempotencyKey,
                outboxResult,
                CasinoConfig.IdempotencyTimeToLivePsp
            );
            return System.Text.Json.JsonSerializer.Deserialize<WithdrawReply>(outboxResult)!;
        }

        ReserveReply reserveResult = await _ledger.ReserveAsync(
            new ReserveRequest
            {
                PlayerId = request.PlayerId,
                Amount = request.Amount,
                IdempotencyKey = IdempotencyKeys.PspWithdraw(request.ProviderReference)
            }
        );
        if (!reserveResult.Success)
            return new WithdrawReply { Success = false, Error = reserveResult.Error };

        CommitReply commitResult = await _ledger.CommitAsync(
            new CommitRequest { TransactionId = reserveResult.TransactionId }
        );
        if (!commitResult.Success)
        {
            await _ledger.RollbackAsync(
                new RollbackRequest { TransactionId = reserveResult.TransactionId }
            );
            return new WithdrawReply { Success = false, Error = ErrorCodes.CommitFailed };
        }

        Guid paymentId = Guid.NewGuid();
        Guid playerGuid = Guid.Parse(request.PlayerId);

        Payment payment =
            new()
            {
                Id = paymentId,
                PlayerId = playerGuid,
                Type = TransactionTypes.Withdraw,
                AmountCents = request.Amount,
                ProviderReference = request.ProviderReference,
                LedgerTransactionId = Guid.Parse(reserveResult.TransactionId)
            };

        _database.Payments.Add(payment);

        WithdrawReply result = new() { Success = true, PaymentId = paymentId.ToString() };
        string resultJson = System.Text.Json.JsonSerializer.Serialize(result);

        PspOutbox outbox =
            new() { ProviderReference = request.ProviderReference, ResultJson = resultJson };

        _database.PspOutbox.Add(outbox);

        await _database.SaveChangesAsync();

        await _redis.Db.StringSetAsync(
            idempotencyKey,
            resultJson,
            CasinoConfig.IdempotencyTimeToLivePsp
        );
        await _redis.Invalidate(CacheKeys.Balance(request.PlayerId));

        return result;
    }
}
