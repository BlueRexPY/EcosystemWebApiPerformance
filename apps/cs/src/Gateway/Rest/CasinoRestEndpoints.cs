using CasinoApi.Casino;
using CasinoApi.Ledger;
using CasinoApi.Player;
using CasinoApi.Shared;
using GatewayError = CasinoApi.Shared.ErrorCodes;

namespace CasinoApi.Gateway.Rest;

public static class CasinoRestEndpoints
{
    public static void Map(WebApplication application)
    {
        application.MapPost(
            "/casino/authenticate",
            async (
                HttpContext http,
                PlayerService.PlayerServiceClient player,
                LedgerService.LedgerServiceClient ledger
            ) =>
            {
                AuthBody? body = await http.Request.ReadFromJsonAsync<AuthBody>();
                if (body?.Token is null)
                    return Results.BadRequest(GatewayError.MissingToken);

                string? playerId = await SessionResolver.ResolveSessionPlayer(body.Token, player);
                if (playerId is null)
                    return Results.Json(
                        new { error = GatewayError.InvalidSession },
                        statusCode: 401
                    );

                GetPlayerReply playerReply = await player.GetPlayerAsync(
                    new GetPlayerRequest { PlayerId = playerId }
                );
                GetBalanceReply balanceReply = await ledger.GetBalanceAsync(
                    new GetBalanceRequest { PlayerId = playerId }
                );
                return Results.Json(
                    new
                    {
                        player_id = playerId,
                        username = playerReply.Username,
                        balance = balanceReply.Balance,
                        reserved = balanceReply.Reserved,
                        kyc = playerReply.KycStatus
                    }
                );
            }
        );

        application.MapPost(
            "/casino/callback",
            async (HttpContext http, CasinoService.CasinoServiceClient casino) =>
            {
                CallbackBody? callbackBody = await http.Request.ReadFromJsonAsync<CallbackBody>();
                if (callbackBody is null)
                    return Results.BadRequest(GatewayError.InvalidBody);

                return callbackBody.Type switch
                {
                    RestCallbackTypes.Bet
                        => Results.Json(
                            await casino.BetAsync(
                                new BetRequest
                                {
                                    SessionToken =
                                        callbackBody.Token ?? GameDefaults.DefaultSessionToken,
                                    ProviderTransactionId =
                                        callbackBody.TransactionId ?? Guid.NewGuid().ToString(),
                                    Amount = callbackBody.AmountCents,
                                    GameId = callbackBody.GameId ?? NumericDefaults.DefaultGameId,
                                    RoundId = callbackBody.RoundId ?? Guid.NewGuid().ToString()
                                }
                            )
                        ),
                    RestCallbackTypes.Win
                        => Results.Json(
                            await casino.WinAsync(
                                new WinRequest
                                {
                                    SessionToken =
                                        callbackBody.Token ?? GameDefaults.DefaultSessionToken,
                                    ProviderTransactionId =
                                        callbackBody.TransactionId ?? Guid.NewGuid().ToString(),
                                    Amount = callbackBody.AmountCents,
                                    GameId = callbackBody.GameId ?? NumericDefaults.DefaultGameId,
                                    RoundId = callbackBody.RoundId ?? Guid.NewGuid().ToString()
                                }
                            )
                        ),
                    RestCallbackTypes.Rollback
                        => Results.Json(
                            await casino.RollbackAsync(
                                new CasinoRollbackRequest
                                {
                                    ProviderTransactionId = callbackBody.TransactionId ?? ""
                                }
                            )
                        ),
                    _ => Results.BadRequest(GatewayError.UnknownType)
                };
            }
        );
    }
}
