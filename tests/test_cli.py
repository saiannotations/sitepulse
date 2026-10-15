"""Tests for CLI wiring: output formats and exit codes (checks are faked)."""

from sitepulse.checks.base import Check, Result, Severity
from sitepulse.cli import main


class AlwaysPass(Check):
    name = "fakepass"
    description = "Test double."

    def run(self, url, timeout=10.0):
        result = Result(check_name=self.name)
        result.add(Severity.PASS, "all good")
        return result


class AlwaysCritical(Check):
    name = "fakecritical"
    description = "Test double."

    def run(self, url, timeout=10.0):
        result = Result(check_name=self.name)
        result.add(Severity.CRITICAL, "everything is broken")
        return result


def _run_cli(args, capsys, monkeypatch):
    import sitepulse.cli as cli_module

    monkeypatch.setitem(cli_module.CHECKS, "fakepass", AlwaysPass)
    monkeypatch.setitem(cli_module.CHECKS, "fakecritical", AlwaysCritical)
    code = main(args)
    return code, capsys.readouterr().out


def test_human_output_and_zero_exit_on_pass(capsys, monkeypatch):
    code, out = _run_cli(["check", "https://example.com", "--checks", "fakepass"], capsys, monkeypatch)
    assert code == 0
    assert "[PASS]" in out
    assert "fakepass" in out


def test_json_output(capsys, monkeypatch):
    import json

    code, out = _run_cli(
        ["check", "https://example.com", "--checks", "fakepass", "--json"], capsys, monkeypatch
    )
    assert code == 0
    payload = json.loads(out)
    assert payload[0]["check"] == "fakepass"
    assert payload[0]["worst"] == "pass"


def test_critical_fails_by_default(capsys, monkeypatch):
    code, _ = _run_cli(["check", "https://example.com", "--checks", "fakecritical"], capsys, monkeypatch)
    assert code == 2


def test_fail_on_warning_flag(capsys, monkeypatch):
    code, _ = _run_cli(
        ["check", "https://example.com", "--checks", "fakepass", "--fail-on", "warning"],
        capsys,
        monkeypatch,
    )
    assert code == 0  # worst is pass, below the warning threshold


def test_redirect_chain_shown_in_human_output(capsys, monkeypatch):
    class Redirecty(Check):
        name = "redirecty"
        description = "Test double."

        def run(self, url, timeout=10.0):
            result = Result(check_name=self.name)
            result.add(
                Severity.WARNING,
                "Long redirect chain (2 hops).",
                redirect_chain=[
                    "http://example.com",
                    "https://example.com",
                    "https://www.example.com",
                ],
            )
            return result

    import sitepulse.cli as cli_module

    monkeypatch.setitem(cli_module.CHECKS, "redirecty", Redirecty)
    code, out = _run_cli(["check", "https://example.com", "--checks", "redirecty"], capsys, monkeypatch)
    assert code == 0
    assert "http://example.com -> https://example.com -> https://www.example.com" in out
