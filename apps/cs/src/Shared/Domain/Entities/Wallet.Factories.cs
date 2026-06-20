namespace CasinoApi.Shared.Entities;

public sealed partial class Wallet
{
    #region Factory methods

    public static Wallet CreateNew(Guid playerId, long initialBalance = 0)
    {
        return new Wallet
        {
            PlayerId = playerId,
            Balance = initialBalance,
            Reserved = 0,
            Version = 1
        };
    }

    #endregion
}
