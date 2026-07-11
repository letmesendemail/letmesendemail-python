# Changelog

## Unreleased

- Webhook signature verification: use raw HMAC bytes (not hex), strict Base64
  validation on the secret, and empty-secret rejection.
- Exact User-Agent test compares against `importlib.metadata.version("letmesendemail")`.
- Resource tests for Emails, Contacts, Domains, Contact Categories, and Email
  Topics covering every operation with exact request assertions.
- Mocked `time.sleep` assertions in retry tests validate delay amounts and call
  counts for network errors, rate limits, 500s, exhaustion, and safe methods.
- Python 3.9 added to CI workflow (3.9–3.13 matrix).
- README rewritten with full resource documentation, attachment examples,
  retry semantics, pagination docs, error type table, and webhook guide.
- publish-guide corrected: no `twine yank` command (PyPI web UI only),
  publishing is always manual.

## 0.1.0 — 2026-07-09

- Initial release.
- Emails API: send, send_with_template, verify, list, get.
- Domains API: list, get, verify.
- Contacts API: create, list, get, update, delete.
- Contact Categories API: create, list, get, update, delete.
- Email Topics API: create, list, get, update, delete.
- Webhook signature verification.
- Structured error classes.
- httpx-based HTTP transport with configurable timeout and base URL.
