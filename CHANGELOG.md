# Changelog

## 0.2.1 — 2026-07-13

- Added comprehensive serialization tests for every public response model,
  nested models, pagination metadata, optional values, defensive copies, and
  standard JSON encoding.
- Documented `to_dict()` for application storage and serialization workflows.
- Documented that the public `SendAttachment` request type is already a plain,
  JSON-serializable dictionary.
- Replaced undocumented webhook event payloads in tests and documentation with
  generic verified payload data.
- Updated the runnable send example to require `LETMESENDEMAIL_API_KEY`, close
  the client deterministically, and handle SDK errors without a fake-key fallback.

## 0.2.0 — 2026-07-11

- Added `to_dict()` method to every response model for dictionary serialization.
- Added comprehensive `docs/docs.md` user manual covering all resources,
  configuration, retries, errors, webhooks, and pagination.
- README now links to the full user manual.
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
