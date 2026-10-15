"""DNS health check.

Verifies the domain resolves to IP addresses, and that it has at least two
distinct nameservers (a single nameserver is a single point of failure).
"""

from __future__ import annotations

import socket
from urllib.parse import urlparse

import dns.resolver

from sitepulse.checks.base import Check, Result, Severity


class DNSCheck(Check):
    name = "dns"
    description = "Checks DNS resolution and nameserver redundancy."

    def run(self, url: str, timeout: float = 10.0) -> Result:
        result = Result(check_name=self.name)
        hostname = urlparse(url).hostname or ""
        if not hostname:
            result.add(Severity.CRITICAL, f"Could not parse a hostname from {url}.")
            return result

        # 1. Does it resolve?
        try:
            _, _, addresses = socket.gethostbyname_ex(hostname)
        except socket.gaierror as exc:
            result.add(
                Severity.CRITICAL,
                f"{hostname} does not resolve to any IP address: {exc}.",
                hostname=hostname,
            )
            return result
        result.add(
            Severity.PASS,
            f"{hostname} resolves to {len(addresses)} address(es): {', '.join(addresses[:4])}.",
            hostname=hostname,
            addresses=addresses,
        )

        # 2. Nameserver redundancy.
        try:
            resolver = dns.resolver.Resolver()
            resolver.lifetime = timeout
            answers = resolver.resolve(hostname, "NS")
            nameservers = sorted({rdata.to_text().rstrip(".") for rdata in answers})
        except Exception as exc:  # DNS can fail in many ways; report, don't crash
            result.add(
                Severity.WARNING,
                f"Could not read NS records for {hostname}: {exc}.",
                hostname=hostname,
            )
            return result

        if len(nameservers) < 2:
            result.add(
                Severity.WARNING,
                f"Only {len(nameservers)} nameserver(s) found ({', '.join(nameservers) or 'none'}) — "
                "use at least two so one outage can't take the site down.",
                nameservers=nameservers,
            )
        else:
            result.add(
                Severity.PASS,
                f"{len(nameservers)} nameservers found — good redundancy.",
                nameservers=nameservers,
            )
        return result
