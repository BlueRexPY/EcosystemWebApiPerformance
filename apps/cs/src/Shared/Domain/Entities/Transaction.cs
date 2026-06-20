using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared.Entities;

[Table("transactions")]
[Index(nameof(PlayerId))]
[Index(nameof(IdempotencyKey), IsUnique = true)]
public sealed partial class Transaction
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

    [Column("idempotency_key"), MaxLength(ColumnLengths.IdempotencyKey)]
    public string? IdempotencyKey { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    #endregion
}
