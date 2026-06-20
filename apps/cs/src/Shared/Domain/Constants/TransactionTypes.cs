namespace CasinoApi.Shared;

/// <summary>Transaction type constants used across all services.</summary>
public static class TransactionTypes
{
    public const string Reserve = "reserve";
    public const string Commit = "commit";
    public const string Settle = "settle";
    public const string Rollback = "rollback";
    public const string Bet = "bet";
    public const string Win = "win";
    public const string Deposit = "deposit";
    public const string Withdraw = "withdraw";
}
