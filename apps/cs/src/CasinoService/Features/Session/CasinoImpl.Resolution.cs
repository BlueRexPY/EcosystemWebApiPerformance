using CasinoApi.Player;
using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.CasinoService;

public sealed partial class CasinoImpl
{
    private async Task<string?> ResolveSessionPlayer(string sessionToken)
    {
        if (!sessionToken.StartsWith(GameDefaults.SessionTokenPrefix))
            return null;
        string numberPart = sessionToken[GameDefaults.SessionTokenPrefix.Length..];
        if (
            !int.TryParse(numberPart, out int playerNumber)
            || playerNumber < GameDefaults.MinPlayerNumber
            || playerNumber > GameDefaults.MaxPlayerNumber
        )
            return null;

        string username = GameDefaults.Username(playerNumber);
        GetPlayerReply result = await _player.GetPlayerByUsernameAsync(
            new GetPlayerByUsernameRequest { Username = username }
        );
        return result.Found ? result.PlayerId : null;
    }

    private async Task<string?> CheckOutbox(string providerTransactionId)
    {
        CasinoOutbox? outbox = await _database
            .CasinoOutbox.AsNoTracking()
            .FirstOrDefaultAsync(o => o.ProviderTransactionId == providerTransactionId);
        return outbox?.ResultJson;
    }
}
