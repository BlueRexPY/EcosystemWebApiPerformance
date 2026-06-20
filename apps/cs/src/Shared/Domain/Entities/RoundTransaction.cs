using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared.Entities;

[Table("round_transactions")]
[Index(nameof(ProviderTransactionId), IsUnique = true)]
public sealed partial class RoundTransaction
{
    #region Properties

    [Key, Column("id")]
    public required Guid Id { get; set; }

    [Column("player_id")]
    public required Guid PlayerId { get; set; }

    [Column("provider_transaction_id"), MaxLength(ColumnLengths.ProviderIdentifier), Required]
    public required string ProviderTransactionId { get; set; }

    [Column("type"), MaxLength(ColumnLengths.TransactionType), Required]
    public required string Type { get; set; }

    [Column("amount_cents")]
    public long AmountCents { get; set; }

    [Column("game_id"), MaxLength(ColumnLengths.GameIdentifier)]
    public string? GameId { get; set; }

    [Column("round_id"), MaxLength(ColumnLengths.GameIdentifier)]
    public string? RoundId { get; set; }

    [Column("ledger_transaction_id")]
    public required Guid LedgerTransactionId { get; set; }

    #endregion
}
