using CasinoApi.Shared.Entities;
using Microsoft.EntityFrameworkCore;

namespace CasinoApi.Shared;

public sealed class PlayerDbContext : DbContext
{
    public PlayerDbContext(DbContextOptions<PlayerDbContext> options)
        : base(options) { }

    public DbSet<Entities.Player> Players => Set<Entities.Player>();
}
