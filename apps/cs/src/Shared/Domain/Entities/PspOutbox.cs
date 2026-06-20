using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CasinoApi.Shared.Entities;

[Table("psp_outbox")]
public sealed partial class PspOutbox
{
    #region Properties

    [Key, Column("provider_ref"), MaxLength(ColumnLengths.ProviderIdentifier)]
    public string ProviderReference { get; set; } = null!;

    [Column("result_json", TypeName = "jsonb")]
    public string ResultJson { get; set; } = null!;

    #endregion
}
