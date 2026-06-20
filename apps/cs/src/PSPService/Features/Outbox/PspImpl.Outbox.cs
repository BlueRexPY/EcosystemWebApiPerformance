using CasinoApi.Shared;
using CasinoApi.Shared.Entities;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.PSPService;

public sealed partial class PspImpl
{
    private async Task<string?> CheckOutbox(string providerReference)
    {
        PspOutbox? outbox = await _database
            .PspOutbox.AsNoTracking()
            .FirstOrDefaultAsync(o => o.ProviderReference == providerReference);
        return outbox?.ResultJson;
    }
}
