namespace CasinoApi.Shared;

/// <summary>Error codes returned in gRPC replies.</summary>
public static class ErrorCodes
{
    public const string InvalidSession = "invalid_session";
    public const string PlayerNotFound = "player_not_found";
    public const string LockTimeout = "lock_timeout";
    public const string InsufficientFunds = "insufficient_funds";
    public const string VersionConflict = "version_conflict";
    public const string InternalError = "internal_error";
    public const string TxNotFound = "tx_not_found";
    public const string CommitFailed = "commit_failed";
    public const string RollbackFailed = "rollback_failed";
    public const string RoundTxNotFound = "round_tx_not_found";
    public const string MissingToken = "missing token";
    public const string InvalidBody = "invalid body";
    public const string UnknownType = "unknown type";
}
