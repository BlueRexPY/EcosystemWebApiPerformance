-- Create Wallets Table (The Ledger Source of Truth)
CREATE TABLE IF NOT EXISTS wallets (
    player_id VARCHAR(64) PRIMARY KEY,
    balance NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Ledger Entries Table (Strict Append-Only History)
CREATE TABLE IF NOT EXISTS ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(64) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    player_id VARCHAR(64) NOT NULL REFERENCES wallets(player_id),
    amount NUMERIC(18, 4) NOT NULL,
    type VARCHAR(10) NOT NULL, -- 'BET' or 'WIN'
    provider_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optimize queries searching historical logs per player
CREATE INDEX idx_ledger_player ON ledger_entries(player_id);

-- Generate Seed Data: 100,000 Players with random balances ranging from €100 to €10,100
INSERT INTO wallets (player_id, balance, currency)
SELECT
    'usr_' || seq AS player_id,
    (100 + (random() * 10000))::NUMERIC(18,4) AS balance,
    'EUR' AS currency
FROM generate_series(1, 100000) AS seq;
