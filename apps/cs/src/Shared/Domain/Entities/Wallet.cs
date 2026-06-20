using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CasinoApi.Shared.Entities;

[Table("wallets")]
public sealed partial class Wallet
{
    #region Properties

    [Key, Column("player_id")]
    public required Guid PlayerId { get; set; }

    [Column("balance")]
    public long Balance { get; private set; }

    [Column("reserved")]
    public long Reserved { get; private set; }

    [Column("version"), ConcurrencyCheck]
    public int Version { get; private set; }

    #endregion
}
