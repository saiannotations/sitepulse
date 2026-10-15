# Contributing to SitePulse

Thank you for helping make the web healthier! This guide covers everything you
need to contribute, whether it's your first open-source PR or your fiftieth.

## Quick start

```bash
git clone https://github.com/saiannotations/sitepulse.git
cd sitepulse
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest          # run the test suite — everything should pass
python -m sitepulse check https://example.com   # try it out
```

## How to add a new check (the most common contribution)

Every check is a small, self-contained plugin. Here's the whole recipe:

1. **Create the module** — add `sitepulse/checks/mycheck.py`:

   ```python
   from sitepulse.checks.base import Check, Result, Severity

   class MyCheck(Check):
       name = "mycheck"                       # short, lowercase, no spaces
       description = "One-line plain-English description."

       def run(self, url: str, timeout: float = 10.0) -> Result:
           result = Result(check_name=self.name)
           # ... do the work ...
           result.add(Severity.PASS, "Everything looks good.")
           result.add(Severity.WARNING, "Worth fixing soon: ...")
           result.add(Severity.CRITICAL, "Fix now: ...")
           return result
   ```

2. **Never raise on expected problems.** Timeouts, DNS failures, refused
   connections — turn them into findings (`Severity.CRITICAL` or
   `Severity.WARNING`), never exceptions. The CLI runs every check in one
   pass; one crashing check shouldn't kill the whole report.

3. **Register it** in `sitepulse/checks/registry.py` by adding your class to
   the `CHECKS` dict. It becomes instantly available via
   `--checks mycheck` and in the GitHub Action.

4. **Write tests** in `tests/test_mycheck.py`. Do NOT hit the real internet —
   mock network calls with `unittest.mock` (see `tests/test_http.py` for the
   pattern). Your PR must keep `pytest` green.

5. **Document it** — add a row to the checks table in `README.md`.

Good first ideas live in issues labeled [`good first issue`](https://github.com/saiannotations/sitepulse/labels/good%20first%20issue),
or propose your own with the **New check proposal** issue template.

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(checks): add DNS CAA record check`
- `fix(links): don't follow links with javascript: scheme`
- `docs: clarify --fail-on exit codes in README`
- `test: cover redirect chains longer than 3 hops`
- `chore: bump requests to 2.32.4`

Keep the subject under 72 characters, present tense, no trailing period.

## Pull request process

1. Fork the repo and create a branch from `main` (`feat/my-check`,
   `fix/broken-thing`).
2. Fill in the PR template checklist (tests, docs, changelog entry).
3. Make sure `pytest` passes and `ruff check .` is clean.
4. One focused change per PR — easier to review, faster to merge.
5. A maintainer will review within a few days. We may ask for changes;
   that's normal and not a rejection.

## Code style

- Python 3.10+; type hints on all public functions.
- `ruff check .` must pass (line length 100).
- Plain-English messages everywhere: findings are read by humans, so write
  like you'd explain it to a friend ("Certificate expires in 6 days — renew
  immediately", not "ERR_CERT_EXPIRY_THRESHOLD_BREACH").

## Questions?

Open a blank issue or start a discussion — no question is too small.
