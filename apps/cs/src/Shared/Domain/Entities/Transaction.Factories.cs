using CasinoApi.Shared;

namespace CasinoApi.Shared.Entities;

public sealed partial class Transaction
{
    #region Factory methods

    public static Transaction Reserve(Guid playerId, long amountCents, string? idempotencyKey) =>
        new()
        {
            Id = Guid.NewGuid(),
            PlayerId = playerId,
            Type = TransactionTypes.Reserve,
            AmountCents = amountCents,
            IdempotencyKey = idempotencyKey
        };

    public static Transaction Commit(Guid playerId, long amountCents) =>
        new()
        {
            Id = Guid.NewGuid(),
            PlayerId = playerId,
            Type = TransactionTypes.Commit,
            AmountCents = amountCents
        };

    public static Transaction Settle(Guid playerId, long amountCents, string? idempotencyKey) =>
        new()
        {
            Id = Guid.NewGuid(),
            PlayerId = playerId,
            Type = TransactionTypes.Settle,
            AmountCents = amountCents,
            IdempotencyKey = idempotencyKey
        };

    public static Transaction Rollback(Guid playerId, long amountCents) =>
        new()
        {
            Id = Guid.NewGuid(),
            PlayerId = playerId,
            Type = TransactionTypes.Rollback,
            AmountCents = amountCents
        };

    #endregion
}
