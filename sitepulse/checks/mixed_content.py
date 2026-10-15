"""Mixed content check.

A page served over HTTPS that loads scripts, styles, images or iframes over
plain HTTP is "mixed content": browsers may block those resources or warn
visitors, breaking the page or its security.
"""

from __future__ import annotations

from html.parser import HTMLParser

import requests

from sitepulse.checks.base import Check, Result, Severity

MAX_REPORTED = 10


class _ResourceExtractor(HTMLParser):
    """Collects URLs of sub-resources: scripts, styles, images, iframes."""

    def __init__(self) -> None:
        super().__init__()
        self.resources: list[tuple[str, str]] = []  # (tag, url)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "script" and attr.get("src"):
            self.resources.append((tag, attr["src"]))
        elif tag == "img" and attr.get("src"):
            self.resources.append((tag, attr["src"]))
        elif tag == "link" and attr.get("href"):
            self.resources.append((tag, attr["href"]))
        elif tag == "iframe" and attr.get("src"):
            self.resources.append((tag, attr["src"]))
        elif tag == "source" and attr.get("src"):
            self.resources.append((tag, attr["src"]))


class MixedContentCheck(Check):
    name = "mixed_content"
    description = "Detects http:// resources loaded by https:// pages."

    def run(self, url: str, timeout: float = 10.0) -> Result:
        result = Result(check_name=self.name)
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            result.add(
                Severity.CRITICAL,
                f"Could not fetch {url} to scan for mixed content: {exc}.",
            )
            return result

        if not response.url.startswith("https://"):
            result.add(
                Severity.PASS,
                "Page is not served over HTTPS — mixed content does not apply.",
                final_url=response.url,
            )
            return result

        extractor = _ResourceExtractor()
        extractor.feed(response.text)
        insecure = [
            (tag, src)
            for tag, src in extractor.resources
            if src.strip().lower().startswith("http://")
        ]

        if insecure:
            shown = ", ".join(f"<{tag}> {src}" for tag, src in insecure[:MAX_REPORTED])
            more = f" (+{len(insecure) - MAX_REPORTED} more)" if len(insecure) > MAX_REPORTED else ""
            result.add(
                Severity.WARNING,
                f"Found {len(insecure)} insecure http:// resource(s) on this HTTPS page: {shown}{more}.",
                insecure=[{"tag": tag, "url": src} for tag, src in insecure],
            )
        else:
            result.add(
                Severity.PASS,
                "No mixed content: all sub-resources load over HTTPS.",
                resources_scanned=len(extractor.resources),
            )
        return result
