namespace CasinoApi.Gateway.GraphQL;

public record PlayerProfile(
    string Id,
    string Username,
    string KycStatus,
    long Balance,
    long Reserved
);
