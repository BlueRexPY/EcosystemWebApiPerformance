namespace CasinoApi.Shared.Entities;

public sealed partial class Wallet
{
    #region Public methods

    /// <summary>Credit funds directly to balance (settle, win, deposit).</summary>
    public void Credit(long amountCents)
    {
        Balance += amountCents;
        Version++;
    }

    /// <summary>Debit funds from balance (commit reserved).</summary>
    public void Debit(long amountCents)
    {
        Balance -= amountCents;
        Version++;
    }

    /// <summary>Reserve funds from available balance.</summary>
    public void Reserve(long amountCents)
    {
        Reserved += amountCents;
        Version++;
    }

    /// <summary>Release reserved funds back to available.</summary>
    public void Release(long amountCents)
    {
        Reserved -= amountCents;
        Version++;
    }

    /// <summary>Commit reserved funds: deduct from balance AND reserved.</summary>
    public void CommitReserved(long amountCents)
    {
        Balance -= amountCents;
        Reserved -= amountCents;
        Version++;
    }

    public bool HasSufficientBalance(long amountCents) => Balance >= amountCents;

    public bool HasSufficientReserved(long amountCents) => Reserved >= amountCents;

    #endregion
}
