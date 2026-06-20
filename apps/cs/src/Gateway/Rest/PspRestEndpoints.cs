using CasinoApi.Psp;
using CasinoApi.Shared;
using GatewayError = CasinoApi.Shared.ErrorCodes;

namespace CasinoApi.Gateway.Rest;

public static class PspRestEndpoints
{
    public static void Map(WebApplication application)
    {
        application.MapPost(
            "/psp/callback",
            async (HttpContext http, PSPService.PSPServiceClient psp) =>
            {
                PspCallbackBody? pspBody = await http.Request.ReadFromJsonAsync<PspCallbackBody>();
                if (pspBody is null)
                    return Results.BadRequest(GatewayError.InvalidBody);

                string pspPlayerId = pspBody.PlayerId ?? NumericDefaults.DefaultPlayerId;
                return pspBody.Type switch
                {
                    RestCallbackTypes.Deposit
                        => Results.Json(
                            await psp.DepositAsync(
                                new DepositRequest
                                {
                                    PlayerId = pspPlayerId,
                                    Amount =
                                        pspBody.AmountCents ?? NumericDefaults.DefaultDepositAmount,
                                    ProviderReference = pspBody.TransactionId ?? Guid.NewGuid().ToString()
                                }
                            )
                        ),
                    RestCallbackTypes.Withdrawal
                        => Results.Json(
                            await psp.WithdrawAsync(
                                new WithdrawRequest
                                {
                                    PlayerId = pspPlayerId,
                                    Amount =
                                        pspBody.AmountCents
                                        ?? NumericDefaults.DefaultWithdrawAmount,
                                    ProviderReference = pspBody.TransactionId ?? Guid.NewGuid().ToString()
                                }
                            )
                        ),
                    _ => Results.BadRequest(GatewayError.UnknownType)
                };
            }
        );
    }
}
