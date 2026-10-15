"""SSL/TLS certificate expiry check.

Warns when a certificate expires in under 30 days, and raises a critical
finding when it expires in under 7 days (or is already expired).
"""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

from sitepulse.checks.base import Check, Result, Severity

WARN_DAYS = 30
CRITICAL_DAYS = 7


def _days_until_expiry(hostname: str, port: int, timeout: float) -> float:
    """Return days until the server's certificate expires (negative if expired)."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
    # cert['notAfter'] looks like 'Jun  1 12:00:00 2027 GMT'
    expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=timezone.utc
    )
    delta = expires - datetime.now(timezone.utc)
    return delta.total_seconds() / 86400


class SSLCheck(Check):
    name = "ssl"
    description = "Checks that the TLS certificate is valid and not expiring soon."

    def run(self, url: str, timeout: float = 10.0) -> Result:
        result = Result(check_name=self.name)
        parsed = urlparse(url)

        if parsed.scheme != "https":
            result.add(
                Severity.CRITICAL,
                "Site does not use HTTPS, so there is no certificate to check.",
                scheme=parsed.scheme or "(none)",
            )
            return result

        hostname = parsed.hostname or ""
        port = parsed.port or 443
        try:
            days = _days_until_expiry(hostname, port, timeout)
        except ssl.SSLCertVerificationError as exc:
            result.add(
                Severity.CRITICAL,
                f"Certificate failed verification: {exc.verify_message or exc}.",
            )
            return result
        except (socket.timeout, TimeoutError):
            result.add(Severity.CRITICAL, f"Timed out connecting to {hostname}:{port}.")
            return result
        except OSError as exc:
            result.add(
                Severity.CRITICAL,
                f"Could not retrieve the certificate from {hostname}:{port}: {exc}.",
            )
            return result

        if days < 0:
            result.add(
                Severity.CRITICAL,
                f"Certificate EXPIRED {-days:.1f} days ago — browsers will block visitors.",
                days_left=round(days, 1),
            )
        elif days < CRITICAL_DAYS:
            result.add(
                Severity.CRITICAL,
                f"Certificate expires in {days:.1f} days — renew immediately.",
                days_left=round(days, 1),
            )
        elif days < WARN_DAYS:
            result.add(
                Severity.WARNING,
                f"Certificate expires in {days:.1f} days — plan renewal soon.",
                days_left=round(days, 1),
            )
        else:
            result.add(
                Severity.PASS,
                f"Certificate is valid for another {days:.0f} days.",
                days_left=round(days, 1),
            )
        return result
