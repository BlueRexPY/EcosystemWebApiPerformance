namespace CasinoApi.Shared;

/// <summary>Database column length constants. Zero magic numbers in entity attributes.</summary>
public static class ColumnLengths
{
    public const int TransactionType = 16;
    public const int KycStatus = 32;
    public const int GameIdentifier = 64;
    public const int Username = 100;
    public const int ProviderIdentifier = 256;
    public const int PasswordHash = 256;
    public const int IdempotencyKey = 256;
}
