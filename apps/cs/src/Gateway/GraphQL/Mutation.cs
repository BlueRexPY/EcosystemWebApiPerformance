using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using CasinoApi.Player;
using CasinoApi.Shared;
using Microsoft.IdentityModel.Tokens;
using SharedClaimTypes = CasinoApi.Shared.ClaimTypes;

namespace CasinoApi.Gateway.GraphQL;

public class Mutation
{
    private static readonly SymmetricSecurityKey SigningKey =
        new(Encoding.UTF8.GetBytes(AuthDefaults.JwtKey));
    private const string TestPasswordHash = AuthDefaults.TestPasswordHash;

    [GraphQLName(GraphQLOperationNames.Login)]
    public async Task<LoginResult?> Login(
        string username,
        string password,
        [Service] PlayerService.PlayerServiceClient player
    )
    {
        AuthenticateReply authenticateResult = await player.AuthenticateAsync(
            new AuthenticateRequest { Username = username, PasswordHash = TestPasswordHash }
        );

        if (!authenticateResult.Success)
            return null;

        string jsonWebToken = GenerateJwt(authenticateResult.PlayerId, authenticateResult.Username);

        return new LoginResult(
            jsonWebToken,
            new PlayerInfo(authenticateResult.PlayerId, authenticateResult.Username)
        );
    }

    [GraphQLName(GraphQLOperationNames.Signup)]
    public async Task<LoginResult?> Signup(
        string username,
        string password,
        [Service] PlayerService.PlayerServiceClient player
    )
    {
        CreatePlayerReply createResult = await player.CreatePlayerAsync(
            new CreatePlayerRequest { Username = username, PasswordHash = TestPasswordHash }
        );
        if (!createResult.Success)
            return null;

        string jsonWebToken = GenerateJwt(createResult.PlayerId, username);
        return new LoginResult(jsonWebToken, new PlayerInfo(createResult.PlayerId, username));
    }

    [GraphQLName(GraphQLOperationNames.Logout)]
    public bool Logout() => true;

    private static string GenerateJwt(string playerId, string username)
    {
        Claim[] claims =
        [
            new Claim(SharedClaimTypes.Subject, playerId),
            new Claim(SharedClaimTypes.Name, username)
        ];
        JwtSecurityToken jsonWebToken =
            new(
                issuer: AuthDefaults.JwtIssuer,
                claims: claims,
                expires: DateTime.UtcNow.AddHours(AuthDefaults.TokenExpiryHours),
                signingCredentials: new SigningCredentials(
                    SigningKey,
                    SecurityAlgorithms.HmacSha256
                )
            );
        return new JwtSecurityTokenHandler().WriteToken(jsonWebToken);
    }
}
