using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;
using StackExchange.Redis;

namespace CasinoApi.PlayerService;

public sealed partial class PlayerImpl
{
    public override async Task<GetPlayerReply> GetPlayer(
        GetPlayerRequest request,
        ServerCallContext context
    )
    {
        string cacheKey = CacheKeys.Player(request.PlayerId);

        RedisValue cached = await _redis.Db.StringGetAsync(cacheKey);

        if (cached.HasValue)
            return System.Text.Json.JsonSerializer.Deserialize<GetPlayerReply>(cached.ToString())!;

        Guid playerId = Guid.Parse(request.PlayerId);

        Shared.Entities.Player? player = await _database
            .Players.AsNoTracking()
            .FirstOrDefaultAsync(p => p.Id == playerId);

        if (player is null)
            return new GetPlayerReply { Found = false };

        GetBalanceReply balance = await _ledger.GetBalanceAsync(
            new GetBalanceRequest { PlayerId = request.PlayerId }
        );

        GetPlayerReply result =
            new()
            {
                Found = true,
                PlayerId = player.Id.ToString(),
                Username = player.Username,
                KycStatus = player.KycStatus,
                Balance = balance.Balance,
                Reserved = balance.Reserved
            };

        await _redis.Db.StringSetAsync(
            cacheKey,
            System.Text.Json.JsonSerializer.Serialize(result),
            CasinoConfig.CacheTimeToLiveShort
        );
        return result;
    }

    public override async Task<GetPlayersReply> GetPlayers(
        GetPlayersRequest request,
        ServerCallContext context
    )
    {
        GetPlayersReply reply = new GetPlayersReply();
        foreach (string playerId in request.PlayerIds)
            reply.Players.Add(
                await GetPlayer(new GetPlayerRequest { PlayerId = playerId }, context)
            );
        return reply;
    }

    public override async Task<GetPlayerReply> GetPlayerByUsername(
        GetPlayerByUsernameRequest request,
        ServerCallContext context
    )
    {
        Shared.Entities.Player? player = await _database
            .Players.AsNoTracking()
            .FirstOrDefaultAsync(p => p.Username == request.Username);
        if (player is null)
            return new GetPlayerReply { Found = false };
        return await GetPlayer(new GetPlayerRequest { PlayerId = player.Id.ToString() }, context);
    }
}
