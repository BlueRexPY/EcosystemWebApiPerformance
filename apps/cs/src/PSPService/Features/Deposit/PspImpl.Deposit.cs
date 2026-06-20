using CasinoApi.Ledger;
using CasinoApi.Psp;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;

namespace CasinoApi.PSPService;

public sealed partial class PspImpl
{
    public override async Task<DepositReply> Deposit(
        DepositRequest request,
        ServerCallContext context
    )
    {
        string idempotencyKey = CacheKeys.IdempotencyPsp(request.ProviderReference);
        string? cached = await _redis.GetIdempotencyResult(idempotencyKey);
        if (cached is not null)
            return System.Text.Json.JsonSerializer.Deserialize<DepositReply>(cached)!;

        string? outboxResult = await CheckOutbox(request.ProviderReference);
        if (outboxResult is not null)
        {
            await _redis.Db.StringSetAsync(
                idempotencyKey,
                outboxResult,
                CasinoConfig.IdempotencyTimeToLivePsp
            );
            return System.Text.Json.JsonSerializer.Deserialize<DepositReply>(outboxResult)!;
        }

        SettleReply settleResult = await _ledger.SettleAsync(
            new SettleRequest
            {
                PlayerId = request.PlayerId,
                Amount = request.Amount,
                IdempotencyKey = IdempotencyKeys.PspDeposit(request.ProviderReference)
            }
        );
        if (!settleResult.Success)
            return new DepositReply { Success = false, Error = settleResult.Error };

        Guid paymentId = Guid.NewGuid();
        Guid playerGuid = Guid.Parse(request.PlayerId);

        Payment payment = new Payment
        {
            Id = paymentId,
            PlayerId = playerGuid,
            Type = TransactionTypes.Deposit,
            AmountCents = request.Amount,
            ProviderReference = request.ProviderReference,
            LedgerTransactionId = Guid.Parse(settleResult.TransactionId)
        };
        _database.Payments.Add(payment);

        DepositReply result = new DepositReply { Success = true, PaymentId = paymentId.ToString() };
        string resultJson = System.Text.Json.JsonSerializer.Serialize(result);

        PspOutbox outbox = new PspOutbox
        {
            ProviderReference = request.ProviderReference,
            ResultJson = resultJson
        };
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
