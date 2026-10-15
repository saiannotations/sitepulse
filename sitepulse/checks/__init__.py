"""Built-in health checks. Each check is a self-contained plugin."""

from sitepulse.checks.base import Check, Finding, Result, Severity

__all__ = ["Check", "Finding", "Result", "Severity"]
