-- Casino database: round transactions and outbox schema
CREATE TABLE IF NOT EXISTS round_transactions (
    id                       UUID PRIMARY KEY,
    player_id                UUID NOT NULL,
    provider_transaction_id  VARCHAR(256) NOT NULL UNIQUE,
    type                     VARCHAR(16) NOT NULL,
    amount_cents             BIGINT NOT NULL,
    game_id                  VARCHAR(64),
    round_id                 VARCHAR(64),
    ledger_transaction_id    UUID NOT NULL
);

CREATE TABLE IF NOT EXISTS casino_outbox (
    provider_transaction_id VARCHAR(256) PRIMARY KEY,
    result_json             JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_round_transaction_player ON round_transactions (player_id);
CREATE INDEX IF NOT EXISTS idx_round_transaction_provider ON round_transactions (provider_transaction_id);
