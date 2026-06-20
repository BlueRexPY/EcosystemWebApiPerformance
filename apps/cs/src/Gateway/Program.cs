using System.Text;
using CasinoApi.Gateway.Rest;
using CasinoApi.Shared;
using Grpc.Net.Client;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

string jwtKey = builder.Configuration["Jwt:Key"] ?? AuthDefaults.JwtKey;
builder
    .Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
        };
    });
builder.Services.AddAuthorization();

builder
    .Services.AddGraphQLServer()
    .AddAuthorization()
    .AddQueryType<CasinoApi.Gateway.GraphQL.Query>()
    .AddMutationType<CasinoApi.Gateway.GraphQL.Mutation>();

builder.Services.AddSingleton(
    new RedisStore(CasinoConfig.RedisConnectionString(builder.Configuration))
);

builder.Services.AddSingleton(_ => new CasinoApi.Casino.CasinoService.CasinoServiceClient(
    GrpcChannel.ForAddress(ServiceEndpoints.Casino)
));
builder.Services.AddSingleton(_ => new CasinoApi.Psp.PSPService.PSPServiceClient(
    GrpcChannel.ForAddress(ServiceEndpoints.Psp)
));
builder.Services.AddSingleton(_ => new CasinoApi.Player.PlayerService.PlayerServiceClient(
    GrpcChannel.ForAddress(ServiceEndpoints.Player)
));
builder.Services.AddSingleton(_ => new CasinoApi.Ledger.LedgerService.LedgerServiceClient(
    GrpcChannel.ForAddress(ServiceEndpoints.Ledger)
));

builder.Services.AddHealthChecks().AddRedisHealthCheck();

WebApplication application = builder.Build();
application.UseAuthentication();
application.UseAuthorization();

CasinoRestEndpoints.Map(application);
PspRestEndpoints.Map(application);
application.MapGraphQL();
application.MapHealthChecks("/health");
application.Run();
