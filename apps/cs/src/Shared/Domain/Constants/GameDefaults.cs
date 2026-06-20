namespace CasinoApi.Shared;

/// <summary>Game domain constants — player limits, session tokens, etc.</summary>
public static class GameDefaults
{
    public const string SessionTokenPrefix = "session-player-";
    public const string DefaultSessionToken = "session-player-00001";
    public const string UsernameFormat = "player_{0:000000}";
    public const string DefaultKycStatus = "verified";
    public const int MinPlayerNumber = 1;
    public const int MaxPlayerNumber = 100_000;
    public const int DefaultTransactionLimit = 50;

    public static string Username(int playerNumber) => string.Format(UsernameFormat, playerNumber);
}
