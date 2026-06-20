-- Ledger database: wallets + transactions schema + 100K wallets
-- Uses same deterministic UUIDs as player init script (uuid_generate_v5)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS wallets (
    player_id UUID PRIMARY KEY,
    balance   BIGINT NOT NULL DEFAULT 0,
    reserved  BIGINT NOT NULL DEFAULT 0,
    version   INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id       UUID NOT NULL,
    type            VARCHAR(16) NOT NULL,
    amount_cents    BIGINT NOT NULL,
    idempotency_key VARCHAR(256) UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_transactions_player_id ON transactions (player_id);
CREATE INDEX IF NOT EXISTS idx_transactions_idempotency ON transactions (idempotency_key);

INSERT INTO wallets (player_id, balance, reserved, version)
SELECT
    uuid_generate_v5(uuid_ns_dns(), 'player_' || LPAD(n::text, 6, '0')),
    10000000,
    0,
    1
FROM generate_series(1, 100000) AS n;
