"""CLI entry point for the casino API load testing harness.

Usage:
    # Test a single ecosystem with all scenarios
    python -m clients.loadtest run --ecosystem go

    # Test all ecosystems with a specific scenario
    python -m clients.loadtest run --scenario casino_bet

    # Test with specific client tools
    python -m clients.loadtest run --ecosystem cs --client wrk --client k6

    # Custom concurrency and duration
    python -m clients.loadtest run --ecosystem js --connections 200 --duration 30

    # List available ecosystems and scenarios
    python -m clients.loadtest list

    # Compare ecosystems with py-async (best percentile detail)
    python -m clients.loadtest run --client py-async --ecosystem go --ecosystem cs --ecosystem js
"""

from __future__ import annotations

import argparse
import logging
import sys

from .config import (
    DEFAULT_K6,
    DEFAULT_PYASYNC,
    DEFAULT_WRK,
    ECOSYSTEMS,
    SCENARIOS,
    K6Config,
    PyAsyncConfig,
    WrkConfig,
)
from .formatter import print_result_console, print_summary_table
from .runner import run_all, run_single


class _ColorFormatter(logging.Formatter):
    _RESET = "\033[0m"
    _BOLD = "\033[1m"
    _COLORS: dict[int, str] = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[35m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, "")
        time_str = self.formatTime(record, "%H:%M:%S")
        level = f"{color}{self._BOLD}{record.levelname:<8}{self._RESET}"
        msg = record.getMessage()
        if msg.startswith("✓"):
            msg = f"\033[32m{self._BOLD}{msg}{self._RESET}"
        elif msg.startswith("✗"):
            msg = f"\033[31m{self._BOLD}{msg}{self._RESET}"
        return f"{color}{time_str}{self._RESET} │ {level} │ {msg}"


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(_ColorFormatter())
    logging.root.setLevel(level)
    logging.root.handlers = [handler]
    # Suppress httpx logging — it logs every request at INFO, killing throughput
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def _cmd_list(_args: argparse.Namespace) -> int:
    """List available ecosystems and scenarios."""
    print("\n── Ecosystems ────────────────────────────────────")
    print(f"  {'Key':<6} {'Display Name':<20} {'Port'}")
    print(f"  {'─'*6} {'─'*20} {'─'*6}")
    for eco in ECOSYSTEMS.values():
        print(f"  {eco.key:<6} {eco.display_name:<20} {eco.port}")

    print("\n── Scenarios ─────────────────────────────────────")
    print(f"  {'Name':<22} {'Method':<6} {'Path':<25} {'Label'}")
    print(f"  {'─'*22} {'─'*6} {'─'*25} {'─'*20}")
    for sc in SCENARIOS.values():
        print(f"  {sc.name:<22} {sc.method:<6} {sc.path:<25} {sc.label}")

    print(f"\n── Clients ───────────────────────────────────────")
    print(f"  wrk       — Classic HTTP throughput (avg/stdev/max, no percentiles)")
    print(f"  k6        — Scripted HTTP with p50/p90/p95/p99 trend metrics")
    print(f"  py-async  — Python httpx async with full histogram (p50-p99.9)")

    print(
        f"\n  Total combos: {len(ECOSYSTEMS)} ecosystems × {len(SCENARIOS)} scenarios × 3 clients = {len(ECOSYSTEMS) * len(SCENARIOS) * 3}"
    )

    # Quick health: show what's running
    import subprocess

    r = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
        capture_output=True,
        text=True,
    )
    if r.stdout.strip():
        print("\n── Running Containers ────────────────────────────")
        for line in r.stdout.strip().splitlines():
            print(f"  {line}")
    else:
        print("\n  (No Docker containers running)")

    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    """Run benchmarks."""
    ecosystems = args.ecosystem if args.ecosystem else None
    scenarios = args.scenario if args.scenario else None
    clients = args.client if args.client else None

    # Validate
    if ecosystems:
        for e in ecosystems:
            if e not in ECOSYSTEMS:
                print(
                    f"Error: Unknown ecosystem '{e}'. Use 'list' to see available ecosystems."
                )
                return 1

    if scenarios:
        for s in scenarios:
            if s not in SCENARIOS:
                print(
                    f"Error: Unknown scenario '{s}'. Use 'list' to see available scenarios."
                )
                return 1

    if clients:
        for c in clients:
            if c not in ("wrk", "k6", "py-async"):
                print(f"Error: Unknown client '{c}'. Valid: wrk, k6, py-async")
                return 1

    wrk_cfg = WrkConfig(
        threads=args.threads,
        connections=args.connections,
        duration_seconds=args.duration,
    )
    k6_cfg = K6Config(
        vus=args.vus,
        duration_seconds=args.duration,
    )
    py_cfg = PyAsyncConfig(
        concurrency=args.connections,  # reuse connections for concurrency
        duration_seconds=args.duration,
    )

    # Single ecosystem + single scenario = detailed per-result output
    if ecosystems and len(ecosystems) == 1 and scenarios and len(scenarios) == 1:
        eco = ECOSYSTEMS[ecosystems[0]]
        scenario = SCENARIOS[scenarios[0]]
        results = run_single(eco, scenario, wrk_cfg, k6_cfg, py_cfg, clients=clients)
        for r in results:
            print_result_console(r)
    else:
        results = run_all(
            ecosystems, scenarios, wrk_cfg, k6_cfg, py_cfg, clients=clients
        )

    print_summary_table(results)

    succeeded = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    print(f"\n✓ {succeeded} passed, ✗ {failed} failed")
    print(f"  Results saved to: results/loadtests/")

    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="loadtest",
        description="Casino API Load Testing Harness — wrk · k6 · py-async",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m clients.loadtest list
  python -m clients.loadtest run --ecosystem go
  python -m clients.loadtest run --ecosystem js --scenario casino_bet
  python -m clients.loadtest run --client py-async --ecosystem go --ecosystem cs
  python -m clients.loadtest run --ecosystem js --connections 200 --duration 30
""",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")
    subparsers.required = True

    # ── run ──
    run_parser = subparsers.add_parser("run", help="Run load tests")
    run_parser.add_argument(
        "--ecosystem",
        "-e",
        action="append",
        help="Ecosystem to test (repeatable). Options: js, go, cs. Default: all.",
    )
    run_parser.add_argument(
        "--scenario",
        "-s",
        action="append",
        help="Scenario to test (repeatable). Default: all.",
    )
    run_parser.add_argument(
        "--client",
        "-c",
        action="append",
        help="Client tool to use (repeatable). Options: wrk, k6, py-async. Default: all three.",
    )
    run_parser.add_argument(
        "--threads",
        type=int,
        default=DEFAULT_WRK.threads,
        help=f"wrk threads (default: {DEFAULT_WRK.threads})",
    )
    run_parser.add_argument(
        "--connections",
        type=int,
        default=DEFAULT_WRK.connections,
        help=f"wrk connections / py-async concurrency (default: {DEFAULT_WRK.connections})",
    )
    run_parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=DEFAULT_WRK.duration_seconds,
        help=f"Test duration in seconds (default: {DEFAULT_WRK.duration_seconds})",
    )
    run_parser.add_argument(
        "--vus",
        type=int,
        default=DEFAULT_K6.vus,
        help=f"k6 virtual users (default: {DEFAULT_K6.vus})",
    )

    # ── list ──
    subparsers.add_parser("list", help="List ecosystems, scenarios, and clients")

    args = parser.parse_args(argv)
    _setup_logging(args.verbose)

    if args.command == "run":
        return _cmd_run(args)
    elif args.command == "list":
        return _cmd_list(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
