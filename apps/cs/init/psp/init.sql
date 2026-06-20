-- PSP database: payments and outbox schema
CREATE TABLE IF NOT EXISTS payments (
    id                    UUID PRIMARY KEY,
    player_id             UUID NOT NULL,
    type                  VARCHAR(16) NOT NULL,
    amount_cents          BIGINT NOT NULL,
    provider_ref          VARCHAR(256) NOT NULL UNIQUE,
    ledger_transaction_id UUID NOT NULL
);

CREATE TABLE IF NOT EXISTS psp_outbox (
    provider_ref VARCHAR(256) PRIMARY KEY,
    result_json  JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_payments_player ON payments (player_id);
CREATE INDEX IF NOT EXISTS idx_payments_provider_ref ON payments (provider_ref);
