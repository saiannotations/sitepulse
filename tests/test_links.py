"""Tests for the broken link crawler (network is mocked)."""

from unittest.mock import patch

from sitepulse.checks.base import Severity
from sitepulse.checks.links import LinksCheck

PAGE = """
<html><body>
<a href="/about">About</a>
<a href="/missing">Missing</a>
<a href="https://other-site.com/x">External (ignored)</a>
<a href="mailto:hi@example.com">Mail (ignored)</a>
</body></html>
"""


class FakePage:
    text = PAGE

    def raise_for_status(self):
        pass


def _run(check_results):
    with patch(
        "sitepulse.checks.links.requests.get", return_value=FakePage()
    ), patch(
        "sitepulse.checks.links._check_one",
        side_effect=lambda link, timeout: (link, check_results[link]),
    ):
        return LinksCheck().run("https://example.com")


def test_all_links_working_passes():
    result = _run(
        {
            "https://example.com/about": 200,
            "https://example.com/missing": 200,
        }
    )
    assert result.worst == Severity.PASS
    assert "2" in result.findings[0].message


def test_broken_link_warns_with_details():
    result = _run(
        {
            "https://example.com/about": 200,
            "https://example.com/missing": 404,
        }
    )
    assert result.worst == Severity.WARNING
    assert result.findings[0].details["broken"][0]["url"] == "https://example.com/missing"


def test_timeout_counts_as_broken():
    result = _run(
        {
            "https://example.com/about": 200,
            "https://example.com/missing": "timeout",
        }
    )
    assert result.worst == Severity.WARNING
