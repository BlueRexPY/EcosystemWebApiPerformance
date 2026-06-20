using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared.Entities;

[Table("payments")]
[Index(nameof(ProviderReference), IsUnique = true)]
public sealed partial class Payment
{
    #region Properties

    [Key, Column("id")]
    public required Guid Id { get; set; }

    [Column("player_id")]
    public required Guid PlayerId { get; set; }

    [Column("type"), MaxLength(ColumnLengths.TransactionType), Required]
    public required string Type { get; set; }

    [Column("amount_cents")]
    public long AmountCents { get; set; }

    [Column("provider_ref"), MaxLength(ColumnLengths.ProviderIdentifier), Required]
    public required string ProviderReference { get; set; }

    [Column("ledger_transaction_id")]
    public required Guid LedgerTransactionId { get; set; }

    #endregion
}
