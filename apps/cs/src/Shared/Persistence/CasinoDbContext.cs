using CasinoApi.Shared.Entities;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared;

public sealed class CasinoDbContext : DbContext
{
    public CasinoDbContext(DbContextOptions<CasinoDbContext> options)
        : base(options) { }

    public DbSet<RoundTransaction> RoundTransactions => Set<RoundTransaction>();
    public DbSet<CasinoOutbox> CasinoOutbox => Set<CasinoOutbox>();
}
