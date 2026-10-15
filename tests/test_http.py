"""Tests for the HTTP check (requests is mocked)."""

from datetime import timedelta
from unittest.mock import patch

import requests

from sitepulse.checks.base import Severity
from sitepulse.checks.http import HTTPCheck


class FakeResponse:
    def __init__(self, status_code=200, history=None, elapsed=0.5, url="https://example.com"):
        self.status_code = status_code
        self.history = history or []
        self.elapsed = timedelta(seconds=elapsed)
        self.url = url


def _mock_get(response=None, exc=None):
    if exc:
        def raiser(*a, **k):
            raise exc
        return patch("sitepulse.checks.http.requests.get", raiser)
    return patch("sitepulse.checks.http.requests.get", return_value=response)


def test_healthy_site_passes():
    with _mock_get(FakeResponse(200, elapsed=0.4)):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.PASS


def test_server_error_is_critical():
    with _mock_get(FakeResponse(503)):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.CRITICAL


def test_client_error_warns():
    with _mock_get(FakeResponse(404)):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.WARNING


def test_long_redirect_chain_warns():
    history = [FakeResponse(301, url=f"https://example.com/{i}") for i in range(5)]
    with _mock_get(FakeResponse(200, history=history)):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.WARNING
    assert "redirect" in result.findings[0].message


def test_slow_response_warns():
    with _mock_get(FakeResponse(200, elapsed=5.0)):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.WARNING
    assert "Slow response" in result.findings[-1].message


def test_timeout_is_critical():
    with _mock_get(exc=requests.exceptions.Timeout()):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.CRITICAL


def test_connection_error_is_critical():
    with _mock_get(exc=requests.exceptions.ConnectionError("dns fail")):
        result = HTTPCheck().run("https://example.com")
    assert result.worst == Severity.CRITICAL
