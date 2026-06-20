using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Grpc.Core;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.PlayerService;

public sealed partial class PlayerImpl
{
    public override async Task<AuthenticateReply> Authenticate(
        AuthenticateRequest request,
        ServerCallContext context
    )
    {
        CasinoApi.Shared.Entities.Player? player = await _database
            .Players.AsNoTracking()
            .FirstOrDefaultAsync(p =>
                p.Username == request.Username && p.PasswordHash == request.PasswordHash
            );
        if (player is null)
            return new AuthenticateReply { Success = false };

        return new AuthenticateReply
        {
            Success = true,
            PlayerId = player.Id.ToString(),
            Username = player.Username
        };
    }

    public override async Task<CreatePlayerReply> CreatePlayer(
        CreatePlayerRequest request,
        ServerCallContext context
    )
    {
        Guid playerId = Guid.NewGuid();
        CasinoApi.Shared.Entities.Player player = new CasinoApi.Shared.Entities.Player
        {
            Id = playerId,
            Username = request.Username,
            PasswordHash = request.PasswordHash,
            KycStatus = GameDefaults.DefaultKycStatus
        };
        _database.Players.Add(player);
        await _database.SaveChangesAsync();

        await _ledger.EnsureWalletAsync(new EnsureWalletRequest { PlayerId = playerId.ToString() });

        return new CreatePlayerReply { Success = true, PlayerId = playerId.ToString() };
    }
}
