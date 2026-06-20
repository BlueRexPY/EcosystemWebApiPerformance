# Multi-stage Docker build for the C# Casino API
# Builds all 5 services into a single image, selectable via SERVICE env var.

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY CasinoApi.sln .
COPY src/Shared/Shared.csproj src/Shared/
COPY src/PlayerService/PlayerService.csproj src/PlayerService/
COPY src/LedgerService/LedgerService.csproj src/LedgerService/
COPY src/CasinoService/CasinoService.csproj src/CasinoService/
COPY src/PSPService/PSPService.csproj src/PSPService/
COPY src/Gateway/Gateway.csproj src/Gateway/
COPY proto/ proto/
COPY . .
RUN dotnet publish src/Gateway/Gateway.csproj -c Release -o /out/gateway
RUN dotnet publish src/PlayerService/PlayerService.csproj -c Release -o /out/player
RUN dotnet publish src/LedgerService/LedgerService.csproj -c Release -o /out/ledger
RUN dotnet publish src/CasinoService/CasinoService.csproj -c Release -o /out/casino
RUN dotnet publish src/PSPService/PSPService.csproj -c Release -o /out/psp

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /out /out

ENV SERVICE=gateway
# ponytail: single image, SERVICE env picks which binary to run.
# docker run -e SERVICE=gateway -p 3002:3002 casino-cs
# docker run -e SERVICE=ledger  -p 5002:5002 casino-cs
CMD if [ "$SERVICE" = "gateway" ]; then dotnet /out/gateway/Gateway.dll; \
    elif [ "$SERVICE" = "player" ]; then dotnet /out/player/PlayerService.dll; \
    elif [ "$SERVICE" = "ledger" ]; then dotnet /out/ledger/LedgerService.dll; \
    elif [ "$SERVICE" = "casino" ]; then dotnet /out/casino/CasinoService.dll; \
    elif [ "$SERVICE" = "psp" ]; then dotnet /out/psp/PSPService.dll; \
    else echo "Unknown SERVICE=$SERVICE"; exit 1; fi
