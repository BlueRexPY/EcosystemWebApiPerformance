namespace CasinoApi.Shared;

/// <summary>Authentication constants.</summary>
public static class AuthDefaults
{
    public const string JwtKey = "casino-benchmark-dev-key-min-32-chars!!";
    public const string JwtIssuer = "casino-gateway";

    // ponytail: dev-mode bcrypt hash for "testpass123"
    public const string TestPasswordHash =
        "$2a$12$LJ3m4ys3Lk0TSwHCbQCIXeD8mJ5V0PYMhBxk3kAiPqTRqVFqOe5y";
    public const int TokenExpiryHours = 24;
}
