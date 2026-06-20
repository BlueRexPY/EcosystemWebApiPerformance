using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared.Entities;

[Table("players")]
[Index(nameof(Username), IsUnique = true)]
public sealed partial class Player
{
    #region Properties

    [Key, Column("id")]
    public required Guid Id { get; set; }

    [Column("username"), MaxLength(ColumnLengths.Username), Required]
    public required string Username { get; set; }

    [Column("password_hash"), MaxLength(ColumnLengths.PasswordHash), Required]
    public required string PasswordHash { get; set; }

    [Column("kyc_status"), MaxLength(ColumnLengths.KycStatus), Required]
    public string KycStatus { get; set; } = "verified";

    #endregion
}
