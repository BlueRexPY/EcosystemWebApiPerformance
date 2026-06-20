namespace CasinoApi.Gateway.GraphQL;

public record TransactionRow(string Id, string Type, long AmountCents, DateTime CreatedAt);
