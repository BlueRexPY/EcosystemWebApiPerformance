using CasinoApi.Player;
using CasinoApi.Shared;

namespace CasinoApi.Gateway.Rest;

public static class SessionResolver
{
    public static async Task<string?> ResolveSessionPlayer(
        string sessionToken,
        PlayerService.PlayerServiceClient player
    )
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
        GetPlayerReply usernameResult = await player.GetPlayerByUsernameAsync(
            new GetPlayerByUsernameRequest { Username = username }
        );
        return usernameResult.Found ? usernameResult.PlayerId : null;
    }
}
