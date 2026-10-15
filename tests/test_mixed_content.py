"""Tests for mixed content detection (network is mocked)."""

from unittest.mock import patch

from sitepulse.checks.base import Severity
from sitepulse.checks.mixed_content import MixedContentCheck


class FakePage:
    def __init__(self, html, url="https://example.com"):
        self.text = html
        self.url = url

    def raise_for_status(self):
        pass


def _run(html, url="https://example.com"):
    with patch(
        "sitepulse.checks.mixed_content.requests.get",
        return_value=FakePage(html, url),
    ):
        return MixedContentCheck().run(url)


def test_clean_https_page_passes():
    html = '<html><img src="https://example.com/a.png"><script src="/b.js"></script></html>'
    result = _run(html)
    assert result.worst == Severity.PASS


def test_http_resources_on_https_warn():
    html = (
        '<html><img src="http://cdn.example.com/a.png">'
        '<script src="http://cdn.example.com/b.js"></script></html>'
    )
    result = _run(html)
    assert result.worst == Severity.WARNING
    assert len(result.findings[0].details["insecure"]) == 2


def test_plain_http_page_is_not_applicable():
    html = '<html><img src="http://example.com/a.png"></html>'
    result = _run(html, url="http://example.com")
    assert result.worst == Severity.PASS
    assert "does not apply" in result.findings[0].message
