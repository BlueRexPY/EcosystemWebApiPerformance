using CasinoApi.Shared;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(
        5001,
        listenOptions =>
            listenOptions.Protocols = Microsoft.AspNetCore.Server.Kestrel.Core.HttpProtocols.Http2
    );
});
string connectionString = CasinoConfig.PlayerDatabase(builder.Configuration);
string redisConnectionString = CasinoConfig.RedisConnectionString(builder.Configuration);

builder.Services.AddPlayerDatabase(connectionString);
builder.Services.AddSingleton(new RedisStore(redisConnectionString));
builder.Services.AddGrpc();
builder.Services.AddHealthChecks().AddRedisHealthCheck();

WebApplication application = builder.Build();
application.MapGrpcService<CasinoApi.PlayerService.PlayerImpl>();
application.MapHealthChecks("/health");
application.Run();
