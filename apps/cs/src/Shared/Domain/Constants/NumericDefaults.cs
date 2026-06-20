namespace CasinoApi.Shared;

/// <summary>Numeric defaults — wallet initial state, ID generation prefixes.</summary>
public static class NumericDefaults
{
    public const long InitialBalance = 0;
    public const long InitialReserved = 0;
    public const int InitialWalletVersion = 1;
    public const long DefaultDepositAmount = 50_000;
    public const long DefaultWithdrawAmount = 25_000;
    public const string DefaultGameId = "slot-mega-7";
    public const string DefaultPlayerId = "00000000-0000-0000-0000-000000000001";
}
