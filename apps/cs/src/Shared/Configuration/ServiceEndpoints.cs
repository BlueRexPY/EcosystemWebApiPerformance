namespace CasinoApi.Shared;

/// <summary>gRPC service endpoint addresses (configurable via env vars for Docker).</summary>
public static class ServiceEndpoints
{
    public static string Player =>
        Environment.GetEnvironmentVariable("GRPC_PLAYER") ?? "http://127.0.0.1:5001";
    public static string Ledger =>
        Environment.GetEnvironmentVariable("GRPC_LEDGER") ?? "http://127.0.0.1:5002";
    public static string Casino =>
        Environment.GetEnvironmentVariable("GRPC_CASINO") ?? "http://127.0.0.1:5003";
    public static string Psp =>
        Environment.GetEnvironmentVariable("GRPC_PSP") ?? "http://127.0.0.1:5004";
}
