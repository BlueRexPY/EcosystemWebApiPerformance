"""Ecosystem registry, endpoint definitions, and test payloads.

Central configuration for all three ecosystems and all benchmark scenarios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "loadtests"
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"


# ── Ecosystem registry ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Ecosystem:
    """A runnable API stack."""

    key: str  # short identifier: "go", "cs", "js"
    display_name: str  # "Go + Fiber", "Bun + Elysia", ".NET 9"
    port: int  # HTTP listen port
    dir_name: str  # results subdirectory


ECOSYSTEMS: dict[str, Ecosystem] = {
    "js": Ecosystem("js", "Bun + Elysia", 3000, "BunElysia"),
    "go": Ecosystem("go", "Go + Fiber", 3001, "GoFiber"),
    "cs": Ecosystem("cs", ".NET 9", 3002, "DotNet"),
}


# ── Scenario definitions ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class Scenario:
    """A single benchmark scenario — endpoint + payload + tool."""

    name: str
    method: str  # HTTP method
    path: str  # e.g. /casino/authenticate
    label: str  # human-readable
    description: str = ""
    payload: dict | None = None  # JSON body for POST
    tool: str = "wrk"  # "wrk" | "k6" | "py-async"
    k6_script: str = ""  # relative to SCRIPTS_DIR, for k6 tool
    weight: int = 1  # for mixed-workload mode: relative frequency


# ── Casino API payloads ───────────────────────────────────────────────────────

_AUTH_PAYLOAD = {"token": "test-session-token-12345", "game_id": "slot-mega-7"}

_BET_PAYLOAD = {
    "type": "bet",
    "amount_cents": 1000,
    "transaction_id": "tx-loadtest",
    "round_id": "round-loadtest",
}

_WIN_PAYLOAD = {
    "type": "win",
    "amount_cents": 2500,
    "transaction_id": "tx-loadtest",
    "round_id": "round-loadtest",
}

_ROLLBACK_PAYLOAD = {
    "type": "rollback",
    "transaction_id": "tx-loadtest",
}

_DEPOSIT_PAYLOAD = {
    "type": "deposit",
    "amount_cents": 50000,
    "transaction_id": "tx-loadtest",
}

_WITHDRAWAL_PAYLOAD = {
    "type": "withdrawal",
    "amount_cents": 25000,
    "transaction_id": "tx-loadtest",
}

_GRAPHQL_QUERY = {"query": """
        query PlayerBalance {
            balance {
                amount_cents
                currency
            }
        }
    """}

_GRAPHQL_LOGIN = {
    "query": """
        mutation Login($username: String!, $password: String!) {
            login(username: $username, password: $password) {
                token
                player { id username }
            }
        }
    """,
    "variables": {"username": "player_00001", "password": "testpass123"},
}

_GRAPHQL_ME = {"query": """
        query Me {
            me {
                id
                username
                balance { amount_cents currency }
            }
        }
    """}

_GRAPHQL_TRANSACTIONS = {
    "query": """
        query Transactions($limit: Int!) {
            transactions(limit: $limit) {
                id
                type
                amount_cents
                created_at
            }
        }
    """,
    "variables": {"limit": 50},
}

_GRAPHQL_SIGNUP = {
    "query": """
        mutation Signup($username: String!, $password: String!) {
            signup(username: $username, password: $password) {
                token
                player { id username }
            }
        }
    """,
    "variables": {"username": "player_00001", "password": "testpass123"},
}

_GRAPHQL_LOGOUT = {
    "query": """
        mutation Logout {
            logout
        }
    """,
}


# ── Scenario registry ─────────────────────────────────────────────────────────

SCENARIOS: dict[str, Scenario] = {
    # ── Provider-facing (inbound) ──────────────────────────────────────────
    "casino_auth": Scenario(
        name="casino_auth",
        method="POST",
        path="/casino/authenticate",
        label="Casino Auth",
        description="Provider validates session token + gets balance",
        payload=_AUTH_PAYLOAD,
        tool="wrk",
    ),
    "casino_bet": Scenario(
        name="casino_bet",
        method="POST",
        path="/casino/callback",
        label="Casino Bet",
        description="Provider places a bet",
        payload=_BET_PAYLOAD,
        tool="wrk",
    ),
    "casino_win": Scenario(
        name="casino_win",
        method="POST",
        path="/casino/callback",
        label="Casino Win",
        description="Provider reports a win",
        payload=_WIN_PAYLOAD,
        tool="wrk",
    ),
    "casino_rollback": Scenario(
        name="casino_rollback",
        method="POST",
        path="/casino/callback",
        label="Casino Rollback",
        description="Provider rolls back a transaction",
        payload=_ROLLBACK_PAYLOAD,
        tool="wrk",
    ),
    "psp_deposit": Scenario(
        name="psp_deposit",
        method="POST",
        path="/psp/callback",
        label="PSP Deposit",
        description="PSP adds funds",
        payload=_DEPOSIT_PAYLOAD,
        tool="wrk",
    ),
    "psp_withdrawal": Scenario(
        name="psp_withdrawal",
        method="POST",
        path="/psp/callback",
        label="PSP Withdrawal",
        description="PSP removes funds",
        payload=_WITHDRAWAL_PAYLOAD,
        tool="wrk",
    ),
    # ── Player-facing ──────────────────────────────────────────────────────
    "player_login": Scenario(
        name="player_login",
        method="POST",
        path="/player/graphql",
        label="Player Login",
        description="GraphQL login mutation",
        payload=_GRAPHQL_LOGIN,
        tool="wrk",
    ),
    "player_balance": Scenario(
        name="player_balance",
        method="POST",
        path="/player/graphql",
        label="Player Balance",
        description="GraphQL balance query",
        payload=_GRAPHQL_QUERY,
        tool="wrk",
    ),
    "player_me": Scenario(
        name="player_me",
        method="POST",
        path="/player/graphql",
        label="Player Me",
        description="GraphQL me query",
        payload=_GRAPHQL_ME,
        tool="wrk",
    ),
    "player_transactions": Scenario(
        name="player_transactions",
        method="POST",
        path="/player/graphql",
        label="Player Transactions",
        description="GraphQL transactions query",
        payload=_GRAPHQL_TRANSACTIONS,
        tool="wrk",
    ),
    "player_signup": Scenario(
        name="player_signup",
        method="POST",
        path="/player/graphql",
        label="Player Signup",
        description="GraphQL signup mutation",
        payload=_GRAPHQL_SIGNUP,
        tool="wrk",
    ),
    "player_logout": Scenario(
        name="player_logout",
        method="POST",
        path="/player/graphql",
        label="Player Logout",
        description="GraphQL logout mutation",
        payload=_GRAPHQL_LOGOUT,
        tool="wrk",
    ),
    # ── Mixed workload (py-async only) ─────────────────────────────────────
    "mixed_casino": Scenario(
        name="mixed_casino",
        method="POST",
        path="",  # path varies per sub-scenario
        label="Mixed Casino",
        description="80% bet, 15% win, 5% rollback — realistic casino load",
        tool="py-async",
    ),
    "mixed_full": Scenario(
        name="mixed_full",
        method="POST",
        path="",
        label="Mixed Full",
        description="All endpoints mixed: auth, bet, win, deposit, login, balance",
        tool="py-async",
    ),
    # ── Player journey (py-async only) ────────────────────────────────────
    "player_journey": Scenario(
        name="player_journey",
        method="POST",
        path="",
        label="Player Journey",
        description=(
            "Full stateful player lifecycle: signup → login → deposit → "
            "gameplay (auth→bet→win loop) → check transactions → withdraw → logout. "
            "Random player IDs, random amounts, random round counts per virtual user."
        ),
        tool="py-async",
    ),
}


# ── wrk / k6 defaults ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class WrkConfig:
    threads: int = 2
    connections: int = 120
    duration_seconds: int = 20

    @property
    def duration_flag(self) -> str:
        return f"{self.duration_seconds}s"


@dataclass(frozen=True)
class K6Config:
    vus: int = 120
    duration_seconds: int = 20

    @property
    def duration_flag(self) -> str:
        return f"{self.duration_seconds}s"


@dataclass(frozen=True)
class PyAsyncConfig:
    concurrency: int = 120
    duration_seconds: int = 20
    warmup_seconds: int = 3


DEFAULT_WRK = WrkConfig()
DEFAULT_K6 = K6Config()
DEFAULT_PYASYNC = PyAsyncConfig()


def result_path(eco: Ecosystem, scenario: Scenario, client: str) -> Path:
    """Return the markdown result file path.

    Example: results/loadtests/GoFiber/CasinoAuth_wrk.md
    """
    label_part = scenario.label.replace(" ", "")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR / eco.dir_name / f"{label_part}_{client}.md"
