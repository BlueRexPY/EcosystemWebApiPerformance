using CasinoApi.Shared.Entities;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared;

public sealed class PspDbContext : DbContext
{
    public PspDbContext(DbContextOptions<PspDbContext> options)
        : base(options) { }

    public DbSet<Payment> Payments => Set<Payment>();

    public DbSet<PspOutbox> PspOutbox => Set<PspOutbox>();
}
