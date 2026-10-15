# SitePulse 📡

[![CI](https://github.com/saiannotations/sitepulse/actions/workflows/ci.yml/badge.svg)](https://github.com/saiannotations/sitepulse/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](requirements.txt)

**Is your website healthy?** SitePulse checks the things that silently break
websites — expiring SSL certificates, dead links, missing security headers,
mixed content, and DNS problems — and tells you in plain English.

Built for everyone from solo bloggers to DevOps teams: run it once by hand,
or run it in CI on every deploy so problems fail the build before your
visitors ever see them.

## 60-second quickstart

```bash
git clone https://github.com/saiannotations/sitepulse.git
cd sitepulse
pip install -r requirements.txt
python -m sitepulse check https://example.com
```

## What it checks

| Check | What it does |
|-------|--------------|
| `ssl` | Certificate expiry — warns under 30 days, critical under 7 |
| `http` | Status code, redirect chains, and slow responses |
| `headers` | Security headers audit (HSTS, CSP, X-Frame-Options, …) |
| `links` | Crawls your pages and reports broken links |
| `mixed_content` | Finds `http://` resources on your `https://` pages |
| `dns` | Domain resolution and nameserver redundancy |

Run everything, or pick: `python -m sitepulse check https://example.com --checks ssl,headers`

## Example output

```
SitePulse report for https://example.com
========================================

## ssl
  [WARN] Certificate expires in 21.3 days — plan renewal soon.

## http
  [PASS] OK: HTTP 200 in 0.42s.

## headers
  [FAIL] Missing: strict-transport-security — tells browsers to only ever use HTTPS (stops downgrade attacks).
  [PASS] Present: content-security-policy.

## links
  [WARN] Found 2 broken link(s) out of 34 checked: https://example.com/old-page (404); https://example.com/draft (404).

## mixed_content
  [PASS] No mixed content: all sub-resources load over HTTPS.

## dns
  [PASS] example.com resolves to 2 address(es): 93.184.216.34, 2606:2800:220:1:248:1893:25c8:1946.
  [PASS] 2 nameservers found — good redundancy.
```

Need machines, not humans? `--json` prints the same report as JSON, and
`--fail-on warning|critical` sets the exit code — perfect for CI:

```yaml
# .github/workflows/site-health.yml
- uses: saiannotations/sitepulse@v1
  with:
    url: https://example.com
    fail-on: critical
```

## How to contribute

SitePulse is built to be contributed to. The most valuable contribution is a
**new check** — and it's designed to take an afternoon:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) (the new-check recipe is copy-paste).
2. Pick an issue labeled [`good first issue`](https://github.com/saiannotations/sitepulse/labels/good%20first%20issue) — or propose your own check with the **New check proposal** template.
3. Open a PR. The template checklist walks you through tests, docs, and lint.

Every check is a self-contained plugin implementing one tiny interface
(`name`, `description`, `run(url) -> Result`), so you'll never have to untangle
core code. See [`docs/user-stories.md`](docs/user-stories.md) for who you're
helping and why.

We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind.

## Roadmap

Where we're headed — grab one and make it yours:

- [ ] Uptime monitoring check (is it up *right now*, from multiple regions?)
- [ ] Lighthouse performance/accessibility scores as a check
- [ ] DNS CAA record presence check
- [ ] `--format markdown` report output for pasting into issues
- [ ] Screenshot-on-failure for visual regression hints
- [ ] Scheduled monitoring mode with Slack/email alerts

Have an idea that's not here? Open a **New check proposal** issue.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship it. 💚
