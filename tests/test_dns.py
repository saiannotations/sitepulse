"""Tests for the DNS check (socket and dnspython are mocked)."""

import socket
from unittest.mock import MagicMock, patch

from sitepulse.checks.base import Severity
from sitepulse.checks.dns import DNSCheck


def _rdata(name):
    record = MagicMock()
    record.to_text.return_value = name
    return record


def _run(addresses=None, nameservers=None, gaierror=False, ns_error=False):
    with patch("sitepulse.checks.dns.socket.gethostbyname_ex") as mock_ghe, patch(
        "sitepulse.checks.dns.dns.resolver.Resolver"
    ) as mock_resolver_cls:
        if gaierror:
            mock_ghe.side_effect = socket.gaierror("no such host")
        else:
            mock_ghe.return_value = ("example.com", [], addresses or ["93.184.216.34"])
        resolver = mock_resolver_cls.return_value
        if ns_error:
            resolver.resolve.side_effect = Exception("SERVFAIL")
        else:
            resolver.resolve.return_value = [_rdata(ns) for ns in (nameservers or [])]
        return DNSCheck().run("https://example.com")


def test_healthy_dns_passes():
    result = _run(nameservers=["ns1.example.com.", "ns2.example.com."])
    assert result.worst == Severity.PASS


def test_unresolvable_domain_is_critical():
    result = _run(gaierror=True)
    assert result.worst == Severity.CRITICAL
    assert "does not resolve" in result.findings[0].message


def test_single_nameserver_warns():
    result = _run(nameservers=["ns1.example.com."])
    assert result.worst == Severity.WARNING
    assert "at least two" in result.findings[-1].message
