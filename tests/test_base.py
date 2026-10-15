"""Tests for the Check plugin interface (no network involved)."""

from sitepulse.checks.base import Check, Result, Severity


class DummyCheck(Check):
    name = "dummy"
    description = "Test double."

    def __init__(self, severities):
        self._severities = severities

    def run(self, url, timeout=10.0):
        result = Result(check_name=self.name)
        for severity in self._severities:
            result.add(severity, f"{severity.value} finding")
        return result


def test_result_worst_is_pass_with_no_findings():
    assert Result(check_name="x").worst == Severity.PASS


def test_result_worst_picks_most_severe():
    check = DummyCheck([Severity.PASS, Severity.WARNING, Severity.CRITICAL])
    assert check.run("https://example.com").worst == Severity.CRITICAL


def test_finding_carries_check_name_and_details():
    result = Result(check_name="ssl")
    result.add(Severity.WARNING, "expiring soon", days_left=12.5)
    finding = result.findings[0]
    assert finding.check == "ssl"
    assert finding.details["days_left"] == 12.5
