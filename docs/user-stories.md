# SitePulse User Stories

Who this project serves, and what "done" looks like for each of them.
Stories are written for humans first — if you can't picture the person,
the story isn't finished.

---

## 1. Solo blogger

**As a** solo blogger running a WordPress site,
**I want** to be warned 30 days before my SSL certificate expires,
**so that** my readers never see a browser security warning.

_Acceptance criteria:_
- Running `sitepulse check` surfaces a WARNING when the certificate has fewer than 30 days left.
- The message says plainly how many days remain and what to do ("renew soon").
- With fewer than 7 days left, the finding is CRITICAL.

## 2. Small business owner

**As a** small business owner with no IT staff,
**I want** a plain-English report of what's wrong with my website,
**so that** I can forward it to my web designer and get it fixed.

_Acceptance criteria:_
- Human-readable output uses no jargon without explanation.
- Each finding is one sentence plus what to do about it.
- The report works with zero configuration — just a URL.

## 3. DevOps engineer

**As a** DevOps engineer responsible for a company site,
**I want** to run SitePulse in CI on every deploy,
**so that** broken deploys (expired certs, missing headers, dead links) fail the pipeline before customers see them.

_Acceptance criteria:_
- `--fail-on critical` exits non-zero when any critical finding exists.
- `--json` output is machine-readable for dashboards and alerting.
- The provided GitHub Action runs the check with a one-line workflow step.

## 4. Open-source contributor (first-timer)

**As a** student making my first open-source contribution,
**I want** a step-by-step guide to adding a new check,
**so that** I can open a meaningful PR in an afternoon.

_Acceptance criteria:_
- CONTRIBUTING.md documents the `Check` interface with a copy-paste example.
- Issues labeled `good first issue` are scoped to a single check or flag.
- `pytest` runs the full suite locally with no external services.

## 5. Open-source contributor (experienced)

**As a** experienced contributor,
**I want** a plugin architecture where each check is self-contained,
**so that** I can add, test, and review checks without touching core code.

_Acceptance criteria:_
- New checks only touch `sitepulse/checks/<name>.py`, `registry.py`, tests, and docs.
- The `Check` base class documents its contract (never raise on expected failures).
- CI runs tests and lint on every PR.

## 6. Agency developer

**As a** freelancer managing 20 client sites,
**I want** to check only the checks I care about per client,
**so that** a slow link crawl doesn't block a quick SSL sanity check.

_Acceptance criteria:_
- `--checks ssl,headers` runs just those checks.
- Unknown check names produce a helpful error listing valid options.

## 7. Security-conscious site owner

**As a** site owner who just read about clickjacking,
**I want** an audit of my security headers,
**so that** I know exactly which protections I'm missing and why they matter.

_Acceptance criteria:_
- Each missing header explains in plain English what attack it stops.
- A missing HSTS header on an HTTPS site is CRITICAL; others are WARNING.
- Present headers are reported as PASS so I can see what's already good.

## 8. Content editor

**As a** content editor who reorganized the blog,
**I want** a list of every broken internal link,
**so that** I can fix them before readers (and Google) hit 404s.

_Acceptance criteria:_
- Broken links are listed with their URL and status code.
- Only same-site links are crawled; external sites are left alone.
- Timeouts count as broken and say so.

## 9. HTTPS migrator

**As a** developer migrating a site to HTTPS,
**I want** to find every `http://` resource on my pages,
**so that** browsers don't block scripts and images after the switch.

_Acceptance criteria:_
- `http://` scripts, images, stylesheets, and iframes are flagged as WARNING.
- The finding lists which tag each insecure resource came from.
- Pure-HTTP pages are reported as not applicable, not as failures.

## 10. Infrastructure engineer

**As a** infrastructure engineer after a DNS outage,
**I want** to verify my domain resolves and has redundant nameservers,
**so that** a single DNS failure can't take the site down again.

_Acceptance criteria:_
- Unresolvable domains are CRITICAL with the resolver error included.
- Fewer than two distinct nameservers is a WARNING explaining the risk.
- DNS failures never crash the rest of the report.

## 11. Non-technical stakeholder

**As a** non-technical founder,
**I want** the README to explain the project in 60 seconds,
**so that** I can decide whether to ask my team to adopt it.

_Acceptance criteria:_
- README opens with what it does, who it's for, and one copy-paste quickstart.
- Example output is shown, not just described.
- The roadmap lists what's coming next.

## 12. Maintainer

**As a** maintainer,
**I want** every PR to arrive with tests, docs, and a clean lint run,
**so that** reviewing contributions stays fast and the codebase stays healthy.

_Acceptance criteria:_
- The PR template checklists tests, docs, lint, and no-secrets.
- CI blocks merging when tests or `ruff` fail.
- Commit messages follow Conventional Commits for a readable history.
