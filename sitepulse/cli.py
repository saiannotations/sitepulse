"""Command-line interface for SitePulse."""

from __future__ import annotations

import argparse
import json
import sys

from sitepulse import __version__
from sitepulse.checks.base import Result, Severity
from sitepulse.checks.registry import CHECKS, available_checks

_MARK = {
    Severity.PASS: "[PASS]",
    Severity.WARNING: "[WARN]",
    Severity.CRITICAL: "[FAIL]",
}

_EXIT_FOR = {Severity.PASS: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sitepulse",
        description="Check a website's health: SSL, links, headers, mixed content, DNS.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Run health checks against a URL.")
    check.add_argument("url", help="URL to check, e.g. https://example.com")
    check.add_argument(
        "--checks",
        default=",".join(available_checks()),
        help="Comma-separated checks to run. "
        f"Available: {', '.join(available_checks())}. (default: all)",
    )
    check.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    check.add_argument(
        "--fail-on",
        choices=["warning", "critical"],
        default="critical",
        help="Exit non-zero when findings reach this severity (default: critical).",
    )
    check.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Network timeout in seconds per check (default: 10).",
    )
    return parser


def print_human(url: str, results: list[Result]) -> None:
    print(f"\nSitePulse report for {url}\n{'=' * (21 + len(url))}")
    for result in results:
        print(f"\n## {result.check_name}")
        if not result.findings:
            print("  (no findings)")
        for finding in result.findings:
            print(f"  {_MARK[finding.severity]} {finding.message}")
    print()


def print_json(results: list[Result]) -> None:
    payload = [
        {
            "check": result.check_name,
            "worst": result.worst.value,
            "findings": [
                {
                    "severity": f.severity.value,
                    "message": f.message,
                    "details": f.details,
                }
                for f in result.findings
            ],
        }
        for result in results
    ]
    print(json.dumps(payload, indent=2, default=str))


def _severity_value(name: str) -> Severity:
    return Severity(name)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    wanted = [c.strip() for c in args.checks.split(",") if c.strip()]
    unknown = [c for c in wanted if c not in CHECKS]
    if unknown:
        parser.error(
            f"unknown check(s): {', '.join(unknown)}. "
            f"Available: {', '.join(available_checks())}"
        )

    results = [CHECKS[name]().run(args.url, timeout=args.timeout) for name in wanted]

    if args.json:
        print_json(results)
    else:
        print_human(args.url, results)

    threshold = _severity_value(args.fail_on)
    worst = max(
        (r.worst for r in results),
        key=lambda s: [Severity.PASS, Severity.WARNING, Severity.CRITICAL].index(s),
        default=Severity.PASS,
    )
    order = [Severity.PASS, Severity.WARNING, Severity.CRITICAL]
    if order.index(worst) >= order.index(threshold):
        return _EXIT_FOR[worst]
    return 0


if __name__ == "__main__":
    sys.exit(main())
