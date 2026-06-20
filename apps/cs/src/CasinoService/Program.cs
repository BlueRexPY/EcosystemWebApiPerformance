using CasinoApi.Shared;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(
        5003,
        listenOptions =>
            listenOptions.Protocols = Microsoft.AspNetCore.Server.Kestrel.Core.HttpProtocols.Http2
    );
});
string connectionString = CasinoConfig.CasinoDatabase(builder.Configuration);
string redisConnectionString = CasinoConfig.RedisConnectionString(builder.Configuration);

builder.Services.AddCasinoDatabase(connectionString);
builder.Services.AddSingleton(new RedisStore(redisConnectionString));
builder.Services.AddGrpc();
builder.Services.AddHealthChecks().AddRedisHealthCheck();

WebApplication application = builder.Build();
application.MapGrpcService<CasinoApi.CasinoService.CasinoImpl>();
application.MapHealthChecks("/health");
application.Run();
