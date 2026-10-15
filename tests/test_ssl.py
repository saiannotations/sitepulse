"""Tests for the SSL check (certificate fetching is mocked)."""

from unittest.mock import patch

from sitepulse.checks.base import Severity
from sitepulse.checks.ssl import SSLCheck


@patch("sitepulse.checks.ssl._days_until_expiry", return_value=90.0)
def test_healthy_certificate_passes(mock_days):
    result = SSLCheck().run("https://example.com")
    assert result.worst == Severity.PASS
    assert "90 days" in result.findings[0].message


@patch("sitepulse.checks.ssl._days_until_expiry", return_value=20.0)
def test_expiring_soon_warns(mock_days):
    result = SSLCheck().run("https://example.com")
    assert result.worst == Severity.WARNING


@patch("sitepulse.checks.ssl._days_until_expiry", return_value=3.0)
def test_expiring_imminently_is_critical(mock_days):
    result = SSLCheck().run("https://example.com")
    assert result.worst == Severity.CRITICAL


@patch("sitepulse.checks.ssl._days_until_expiry", return_value=-5.0)
def test_expired_certificate_is_critical(mock_days):
    result = SSLCheck().run("https://example.com")
    assert result.worst == Severity.CRITICAL
    assert "EXPIRED" in result.findings[0].message


def test_plain_http_has_no_certificate_to_check():
    result = SSLCheck().run("http://example.com")
    assert result.worst == Severity.CRITICAL
    assert "HTTPS" in result.findings[0].message
