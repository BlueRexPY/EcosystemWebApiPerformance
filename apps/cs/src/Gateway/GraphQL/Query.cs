using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using Microsoft.IdentityModel.Tokens;
using StackExchange.Redis;
using SharedClaimTypes = CasinoApi.Shared.ClaimTypes;

namespace CasinoApi.Gateway.GraphQL;

/// <summary>
/// Pure BFF — all data via gRPC to backend microservices. No direct DB access.
/// </summary>
public class Query
{
    [GraphQLName(GraphQLOperationNames.Me)]
    public async Task<PlayerProfile?> Me(
        ClaimsPrincipal claims,
        [Service] PlayerService.PlayerServiceClient player,
        RedisStore redis
    )
    {
        string? playerId = claims.FindFirstValue(SharedClaimTypes.Subject);
        if (playerId is null)
            return null;

        string cacheKey = CacheKeys.Player(playerId);
        RedisValue cached = await redis.Db.StringGetAsync(cacheKey);
        if (cached.HasValue)
            return System.Text.Json.JsonSerializer.Deserialize<PlayerProfile>(cached.ToString());

        GetPlayerReply playerReply = await player.GetPlayerAsync(
            new GetPlayerRequest { PlayerId = playerId }
        );
        if (!playerReply.Found)
            return null;

        PlayerProfile profile = new PlayerProfile(
            Id: playerReply.PlayerId,
            playerReply.Username,
            playerReply.KycStatus,
            playerReply.Balance,
            playerReply.Reserved
        );
        await redis.Db.StringSetAsync(
            cacheKey,
            System.Text.Json.JsonSerializer.Serialize(profile),
            CasinoConfig.CacheTimeToLiveShort
        );
        return profile;
    }

    [GraphQLName(GraphQLOperationNames.Transactions)]
    public async Task<List<TransactionRow>> Transactions(
        ClaimsPrincipal claims,
        [Service] LedgerService.LedgerServiceClient ledger,
        int limit = GameDefaults.DefaultTransactionLimit
    )
    {
        string? playerId = claims.FindFirstValue(SharedClaimTypes.Subject);
        if (playerId is null)
            return [];

        ListTransactionsReply reply = await ledger.ListTransactionsAsync(
            new ListTransactionsRequest { PlayerId = playerId, Limit = limit }
        );
        return reply
            .Items.Select(item => new TransactionRow(
                item.Id,
                item.Type,
                item.AmountCents,
                DateTime.Parse(item.CreatedAt)
            ))
            .ToList();
    }
}
