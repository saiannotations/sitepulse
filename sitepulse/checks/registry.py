"""Central registry of available checks.

To add a check, implement :class:`~sitepulse.checks.base.Check` and add it
to ``CHECKS`` below (see CONTRIBUTING.md for the full walkthrough).
"""

from sitepulse.checks.base import Check
from sitepulse.checks.dns import DNSCheck
from sitepulse.checks.headers import HeadersCheck
from sitepulse.checks.http import HTTPCheck
from sitepulse.checks.links import LinksCheck
from sitepulse.checks.mixed_content import MixedContentCheck
from sitepulse.checks.ssl import SSLCheck

CHECKS: dict[str, type[Check]] = {
    "ssl": SSLCheck,
    "http": HTTPCheck,
    "headers": HeadersCheck,
    "links": LinksCheck,
    "mixed_content": MixedContentCheck,
    "dns": DNSCheck,
}


def available_checks() -> list[str]:
    return sorted(CHECKS)
