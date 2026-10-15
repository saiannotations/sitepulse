"""Basic HTTP health check: status code, redirect chain, response time."""

from __future__ import annotations

import requests

from sitepulse.checks.base import Check, Result, Severity

SLOW_SECONDS = 3.0


class HTTPCheck(Check):
    name = "http"
    description = "Checks the site responds with a healthy status code, in good time."

    def run(self, url: str, timeout: float = 10.0) -> Result:
        result = Result(check_name=self.name)
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
        except requests.exceptions.Timeout:
            result.add(Severity.CRITICAL, f"No response from {url} within {timeout}s.")
            return result
        except requests.exceptions.ConnectionError as exc:
            result.add(Severity.CRITICAL, f"Could not connect to {url}: {exc}.")
            return result
        except requests.exceptions.RequestException as exc:
            result.add(Severity.CRITICAL, f"Request to {url} failed: {exc}.")
            return result

        elapsed = response.elapsed.total_seconds()
        chain = [r.url for r in response.history] + [response.url]
        details = {
            "status": response.status_code,
            "redirects": len(response.history),
            "redirect_chain": chain,
            "response_time_s": round(elapsed, 2),
            "final_url": response.url,
        }

        if response.status_code >= 500:
            result.add(
                Severity.CRITICAL,
                f"Server error: {url} returned HTTP {response.status_code}.",
                **details,
            )
        elif response.status_code >= 400:
            result.add(
                Severity.WARNING,
                f"Client error: {url} returned HTTP {response.status_code}.",
                **details,
            )
        elif len(response.history) > 3:
            result.add(
                Severity.WARNING,
                f"Long redirect chain ({len(response.history)} hops) before reaching the page.",
                **details,
            )
        else:
            result.add(
                Severity.PASS,
                f"OK: HTTP {response.status_code} in {elapsed:.2f}s.",
                **details,
            )

        if elapsed > SLOW_SECONDS and response.status_code < 500:
            result.add(
                Severity.WARNING,
                f"Slow response: {elapsed:.2f}s (over the {SLOW_SECONDS:.0f}s budget).",
                **details,
            )
        return result
