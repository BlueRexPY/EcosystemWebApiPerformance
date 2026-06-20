using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CasinoApi.Shared.Entities;

[Table("casino_outbox")]
public sealed partial class CasinoOutbox
{
    #region Properties

    [Key, Column("provider_transaction_id"), MaxLength(ColumnLengths.ProviderIdentifier)]
    public string ProviderTransactionId { get; set; } = null!;

    [Column("result_json", TypeName = "jsonb")]
    public string ResultJson { get; set; } = null!;

    #endregion
}
