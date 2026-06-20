-- Player database: schema + 100,000 players with deterministic UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS players (
    id          UUID PRIMARY KEY,
    username    VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    kyc_status  VARCHAR(32) NOT NULL DEFAULT 'verified'
);
CREATE INDEX IF NOT EXISTS idx_players_username ON players (username);

INSERT INTO players (id, username, password_hash, kyc_status)
SELECT
    uuid_generate_v5(uuid_ns_dns(), 'player_' || LPAD(n::text, 6, '0')),
    'player_' || LPAD(n::text, 6, '0'),
    '$2a$12$LJ3m4ys3Lk0TSwHCbQCIXeD8mJ5V0PYMhBxk3kAiPqTRqVFqOe5y',
    'verified'
FROM generate_series(1, 100000) AS n;
