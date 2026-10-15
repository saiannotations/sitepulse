"""Broken link check.

Fetches the page, collects its links, and verifies each one. Only links on
the same site are followed (we don't want to hammer the whole internet),
and the crawl is capped so a huge page can't run forever.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

from sitepulse.checks.base import Check, Result, Severity

MAX_LINKS = 50
WORKERS = 8


class _LinkExtractor(HTMLParser):
    """Collects href/src URLs from <a>, <img>, <link> and <script> tags."""

    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "a" and attr.get("href"):
            self.links.add(attr["href"])
        elif tag in ("img", "script") and attr.get("src"):
            self.links.add(attr["src"])
        elif tag == "link" and attr.get("href"):
            self.links.add(attr["href"])


def _check_one(link: str, timeout: float) -> tuple[str, int | str]:
    try:
        response = requests.head(link, timeout=timeout, allow_redirects=True)
        if response.status_code == 405:  # some servers reject HEAD; retry with GET
            response = requests.get(link, timeout=timeout, allow_redirects=True)
        return link, response.status_code
    except requests.exceptions.Timeout:
        return link, "timeout"
    except requests.exceptions.RequestException as exc:
        return link, f"error: {exc}"


class LinksCheck(Check):
    name = "links"
    description = "Crawls the page and reports broken links (4xx/5xx, timeouts)."

    def run(self, url: str, timeout: float = 10.0) -> Result:
        result = Result(check_name=self.name)
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            result.add(
                Severity.CRITICAL,
                f"Could not fetch {url} to crawl links: {exc}.",
            )
            return result

        extractor = _LinkExtractor()
        extractor.feed(response.text)

        page_url = response.url.split("#")[0].rstrip("/")
        base_host = urlparse(url).netloc
        same_origin = set()
        for raw in extractor.links:
            absolute = urljoin(url, raw)
            parsed = urlparse(absolute)
            if parsed.scheme not in ("http", "https"):
                continue  # skip mailto:, tel:, javascript:, ...
            clean = absolute.split("#")[0].rstrip("/")
            if not clean or clean == page_url:
                continue  # fragment-only (#section) or self link — not worth checking
            if parsed.netloc == base_host:
                same_origin.add(absolute.split("#")[0])

        to_check = sorted(same_origin)[:MAX_LINKS]
        if not to_check:
            result.add(Severity.PASS, "No same-site links found to check.")
            return result

        broken: list[tuple[str, int | str]] = []
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            for link, status in pool.map(
                lambda target: _check_one(target, timeout), to_check
            ):
                if isinstance(status, int):
                    if status >= 400:
                        broken.append((link, status))
                else:
                    broken.append((link, status))

        if broken:
            shown = "; ".join(f"{link} ({status})" for link, status in broken[:10])
            more = f" (+{len(broken) - 10} more)" if len(broken) > 10 else ""
            result.add(
                Severity.WARNING,
                f"Found {len(broken)} broken link(s) out of {len(to_check)} checked: {shown}{more}.",
                broken=[{"url": link, "status": status} for link, status in broken],
                checked=len(to_check),
            )
        else:
            result.add(
                Severity.PASS,
                f"All {len(to_check)} same-site link(s) are working.",
                checked=len(to_check),
            )
        return result
