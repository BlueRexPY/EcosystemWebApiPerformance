using CasinoApi.Shared.Entities;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared;

public sealed class LedgerDbContext : DbContext
{
    public LedgerDbContext(DbContextOptions<LedgerDbContext> options)
        : base(options) { }

    public DbSet<Wallet> Wallets => Set<Wallet>();
    public DbSet<Transaction> Transactions => Set<Transaction>();
}
