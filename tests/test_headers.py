"""Tests for the security headers audit (requests is mocked)."""

from unittest.mock import patch

from sitepulse.checks.base import Severity
from sitepulse.checks.headers import HeadersCheck


class FakeResponse:
    def __init__(self, headers, url="https://example.com"):
        self.headers = headers
        self.url = url


GOOD_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'self'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


def _run(headers, url="https://example.com"):
    with patch(
        "sitepulse.checks.headers.requests.get",
        return_value=FakeResponse(headers, url),
    ):
        return HeadersCheck().run(url)


def test_all_headers_present_passes():
    result = _run(GOOD_HEADERS)
    assert result.worst == Severity.PASS
    assert len(result.findings) == 5


def test_missing_hsts_is_critical_on_https():
    headers = dict(GOOD_HEADERS)
    del headers["Strict-Transport-Security"]
    result = _run(headers)
    assert result.worst == Severity.CRITICAL


def test_missing_csp_warns():
    headers = dict(GOOD_HEADERS)
    del headers["Content-Security-Policy"]
    result = _run(headers)
    assert result.worst == Severity.WARNING


def test_wrong_nosniff_value_warns():
    headers = dict(GOOD_HEADERS, **{"X-Content-Type-Options": "sniff"})
    result = _run(headers)
    assert result.worst == Severity.WARNING
    assert "nosniff" in result.findings[-1].message
