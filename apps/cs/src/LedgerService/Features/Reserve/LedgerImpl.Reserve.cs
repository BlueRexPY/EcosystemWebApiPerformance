using CasinoApi.Ledger;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.LedgerService;

public sealed partial class LedgerImpl
{
    public override async Task<ReserveReply> Reserve(
        ReserveRequest request,
        ServerCallContext context
    )
    {
        string idempotencyKey = CacheKeys.IdempotencyLedger(request.IdempotencyKey);
        string? cached = await _redis.GetIdempotencyResult(idempotencyKey);
        if (cached is not null)
        {
            _logger.LogDebug("Reserve idempotency hit: {Key}", request.IdempotencyKey);
            return Deserialize<ReserveReply>(cached);
        }

        string lockKey = CacheKeys.ReserveLock(request.PlayerId);
        await using RedisLock? distributedLock = await _redis.AcquireLockAsync(
            lockKey,
            CasinoConfig.LockTimeout
        );
        if (distributedLock is null)
            return new ReserveReply { Success = false, Error = ErrorCodes.LockTimeout };

        await using Microsoft.EntityFrameworkCore.Storage.IDbContextTransaction databaseTransaction =
            await _database.Database.BeginTransactionAsync();

        try
        {
            Guid playerId = Guid.Parse(request.PlayerId);
            Wallet? wallet = await _database
                .Wallets.FromSqlRaw(
                    "SELECT * FROM wallets WHERE player_id = {0}::uuid FOR UPDATE",
                    playerId
                )
                .FirstOrDefaultAsync();

            if (wallet is null)
                return new ReserveReply { Success = false, Error = ErrorCodes.PlayerNotFound };

            if (wallet.Balance < request.Amount)
                return new ReserveReply { Success = false, Error = ErrorCodes.InsufficientFunds };

            int version = wallet.Version;
            Transaction transaction = Transaction.Reserve(
                playerId,
                request.Amount,
                request.IdempotencyKey
            );
            _database.Transactions.Add(transaction);

            wallet.Reserve(request.Amount);
            _database.Entry(wallet).Property(w => w.Version).OriginalValue = version;

            await _database.SaveChangesAsync();
            await databaseTransaction.CommitAsync();

            ReserveReply result = new ReserveReply
            {
                Success = true,
                TransactionId = transaction.Id.ToString(),
                NewBalance = wallet.Balance,
                NewReserved = wallet.Balance - request.Amount
            };

            await _redis.Db.StringSetAsync(
                idempotencyKey,
                Serialize(result),
                CasinoConfig.IdempotencyTimeToLiveCasino
            );
            await _redis.Invalidate(CacheKeys.Balance(request.PlayerId));

            return result;
        }
        catch (DbUpdateConcurrencyException)
        {
            await databaseTransaction.RollbackAsync();
            return new ReserveReply { Success = false, Error = ErrorCodes.VersionConflict };
        }
        catch (Exception exception)
        {
            await databaseTransaction.RollbackAsync();
            _logger.LogError(exception, "Reserve failed for player {PlayerId}", request.PlayerId);
            return new ReserveReply { Success = false, Error = ErrorCodes.InternalError };
        }
    }
}
