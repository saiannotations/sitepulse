"""Security headers audit.

Checks for the headers that protect visitors from common attacks:
HSTS, Content-Security-Policy, X-Frame-Options, X-Content-Type-Options,
and Referrer-Policy.
"""

from __future__ import annotations

import requests

from sitepulse.checks.base import Check, Result, Severity

# header -> (why it matters, severity when missing)
EXPECTED_HEADERS: dict[str, tuple[str, Severity]] = {
    "strict-transport-security": (
        "tells browsers to only ever use HTTPS (stops downgrade attacks)",
        Severity.CRITICAL,
    ),
    "content-security-policy": (
        "limits where scripts and content may load from (stops XSS)",
        Severity.WARNING,
    ),
    "x-frame-options": (
        "stops the page being embedded in iframes on other sites (stops clickjacking)",
        Severity.WARNING,
    ),
    "x-content-type-options": (
        'should be "nosniff" so browsers never guess content types',
        Severity.WARNING,
    ),
    "referrer-policy": (
        "controls how much of the URL leaks to other sites via the Referer header",
        Severity.WARNING,
    ),
}


class HeadersCheck(Check):
    name = "headers"
    description = "Audits security headers (HSTS, CSP, X-Frame-Options, ...)."

    def run(self, url: str, timeout: float = 10.0) -> Result:
        result = Result(check_name=self.name)
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
        except requests.exceptions.RequestException as exc:
            result.add(
                Severity.CRITICAL,
                f"Could not fetch {url} to inspect headers: {exc}.",
            )
            return result

        headers = {k.lower(): v for k, v in response.headers.items()}
        is_https = response.url.startswith("https://")

        for header, (why, severity) in EXPECTED_HEADERS.items():
            value = headers.get(header)
            if value:
                result.add(
                    Severity.PASS,
                    f"Present: {header}.",
                    header=header,
                    value=value,
                )
                continue
            # HSTS only makes sense over HTTPS; don't nag http:// sites for it.
            if header == "strict-transport-security" and not is_https:
                continue
            result.add(
                severity,
                f"Missing: {header} — {why}.",
                header=header,
            )

        # Sanity-check the values we did get.
        xcto = headers.get("x-content-type-options", "")
        if xcto and xcto.lower() != "nosniff":
            result.add(
                Severity.WARNING,
                f'x-content-type-options should be "nosniff", got "{xcto}".',
                header="x-content-type-options",
                value=xcto,
            )
        return result
