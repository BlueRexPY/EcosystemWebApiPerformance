namespace CasinoApi.Shared;

/// <summary>Factory for ledger idempotency keys used by Casino and PSP services.</summary>
public static class IdempotencyKeys
{
    public static string CasinoBet(string providerTransactionId) =>
        $"casino-bet-{providerTransactionId}";

    public static string CasinoWin(string providerTransactionId) =>
        $"casino-win-{providerTransactionId}";

    public static string PspDeposit(string providerReference) => $"psp-deposit-{providerReference}";

    public static string PspWithdraw(string providerReference) =>
        $"psp-withdraw-{providerReference}";
}
