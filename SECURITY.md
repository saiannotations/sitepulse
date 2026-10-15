# Security Policy

## Reporting a vulnerability

**Do not open a public issue** for security vulnerabilities. Instead, email
saiannotations@users.noreply.github.com with:

- A description of the vulnerability
- Steps to reproduce it (a small script is ideal)
- The version or commit you tested against

You can expect an acknowledgement within 72 hours. We'll work with you on a
fix and credit you in the release notes (unless you'd rather stay anonymous).

## Scope

SitePulse itself makes outbound network connections to whatever URL you ask it
to check — that's its job. A report counts as a vulnerability if SitePulse can
be tricked into doing something the user didn't ask for (for example, SSRF via
a crafted redirect, or arbitrary code execution through a malicious check
plugin loaded from an untrusted source).

The demo workflows in this repo are examples only; review them before pointing
them at production systems you don't own, and never scan sites without
permission.

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
