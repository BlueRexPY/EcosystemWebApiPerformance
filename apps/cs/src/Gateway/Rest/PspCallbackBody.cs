namespace CasinoApi.Gateway.Rest;

public record PspCallbackBody(
    string Type,
    long? AmountCents,
    string? PlayerId,
    string? TransactionId
);
