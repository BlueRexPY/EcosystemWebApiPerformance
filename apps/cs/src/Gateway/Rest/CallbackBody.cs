namespace CasinoApi.Gateway.Rest;

public record CallbackBody(
    string Type,
    long AmountCents,
    string? Token,
    string? TransactionId,
    string? GameId,
    string? RoundId
);
