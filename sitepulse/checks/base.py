"""The plugin interface every SitePulse check implements.

To add a new check (see CONTRIBUTING.md):
  1. Create a module in this package, e.g. ``sitepulse/checks/mycheck.py``.
  2. Subclass :class:`Check`, set ``name`` and ``description``.
  3. Implement :meth:`Check.run`, returning a :class:`Result`.
  4. Register it in ``sitepulse/checks/registry.py``.
  5. Add tests under ``tests/`` — no real network calls, use mocks.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """How bad a single finding is."""

    PASS = "pass"  # everything is fine
    WARNING = "warning"  # worth fixing soon
    CRITICAL = "critical"  # fix now — visitors or security are affected


_SEVERITY_ORDER = {
    Severity.PASS: 0,
    Severity.WARNING: 1,
    Severity.CRITICAL: 2,
}


@dataclass
class Finding:
    """One thing a check discovered."""

    check: str  # name of the check that produced this finding
    severity: Severity
    message: str  # plain-English, one sentence
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Result:
    """Everything one check found for a URL."""

    check_name: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def worst(self) -> Severity:
        """The most severe finding, or PASS when there are none."""
        worst = Severity.PASS
        for finding in self.findings:
            if _SEVERITY_ORDER[finding.severity] > _SEVERITY_ORDER[worst]:
                worst = finding.severity
        return worst

    def add(self, severity: Severity, message: str, **details: Any) -> None:
        self.findings.append(
            Finding(check=self.check_name, severity=severity, message=message, details=details)
        )


class Check(ABC):
    """Base class for every SitePulse check plugin."""

    name: str = "base"
    description: str = "Base check (override me)."

    @abstractmethod
    def run(self, url: str, timeout: float = 10.0) -> Result:
        """Run the check against ``url`` and return a :class:`Result`.

        Implementations must never raise on expected problems (timeouts,
        DNS failures, bad certificates): turn them into findings instead.
        """
