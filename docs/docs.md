# letmesend.email Python SDK

The official Python SDK for the [letmesend.email](https://letmesend.email/) API.

## Overview

This SDK provides a complete, idiomatic Python interface to the letmesend.email API.
It supports sending transactional and broadcast emails, managing domains, contacts,
contact categories, and email topics, verifying email addresses, and verifying
webhook signatures.

All HTTP communication uses httpx. Response parsing, error mapping, retry handling,
and pagination are built in.

## Requirements

- Python 3.9 or later
- `httpx` >= 0.25.0

## Installation

```bash
pip install letmesendemail
```

## Authentication

The SDK authenticates using a bearer token (API key). Obtain your API key from
the [letmesend.email](https://letmesend.email/) dashboard.

**Recommended:** Set the API key in your environment:

```bash
export LETMESENDEMAIL_API_KEY=lms_live_your_api_key_here
```

```python
import os

api_key = os.environ.get("LETMESENDEMAIL_API_KEY")
if not api_key:
    raise RuntimeError("LETMESENDEMAIL_API_KEY environment variable is not set.")

from letmesendemail import LetMeSendEmail
client = LetMeSendEmail(api_key=api_key)
```

## Quick Start

```python
import os
from letmesendemail import LetMeSendEmail

api_key = os.environ.get("LETMESENDEMAIL_API_KEY")
if not api_key:
    raise RuntimeError("LETMESENDEMAIL_API_KEY environment variable is not set.")

client = LetMeSendEmail(api_key=api_key)

try:
    email = client.emails.send(
        from_="Acme <hello@acme.com>",
        to=["person@example.com"],
        subject="Welcome",
        html="<p>Hello from letmesend.email</p>",
    )
    print(email.id, email.status)
except Exception as e:
    print(f"Error: {e}")
```

## Client Configuration

### Simple API-Key Client

```python
from letmesendemail import LetMeSendEmail
client = LetMeSendEmail(api_key="lms_live_...")
```

### Custom Configuration

```python
client = LetMeSendEmail(
    api_key="lms_live_...",
    base_url="https://letmesend.email/api/v1",
    timeout_ms=60_000,
    retries=3,
)
```

### Configuration Reference

| Option | Default | Description |
|--------|---------|-------------|
| `api_key` | — | Your letmesend.email API key (required) |
| `base_url` | `https://letmesend.email/api/v1` | API base URL override |
| `timeout_ms` | `30000` | Request timeout in milliseconds; 0 or negative resets to 30000 |
| `retries` | `0` | Maximum retry attempts for idempotent requests; negative resets to 0 |

### User-Agent

The SDK sends a `User-Agent` header in the format `letmesendemail-python/<version>`.
The version is resolved at runtime from installed package metadata via
`importlib.metadata.version("letmesendemail")`. Falls back to `0.0.0` when
the package is not installed.

## Retries

Retries are enabled by setting `retries > 0`. The SDK retries only on transient
failures.

### Eligibility

| Condition | Retried? |
|-----------|----------|
| GET, HEAD, OPTIONS, DELETE | Yes |
| POST, PUT, PATCH without `Idempotency-Key` | No |
| POST, PUT, PATCH with `Idempotency-Key` | Yes |
| Email/domain verification (`/verify`) | No |

### Retryable Failures

- `NetworkError`, `TimeoutError`
- HTTP 408, 429, 500, 502, 503, 504

### Backoff

- **Network/timeout/5xx errors:** Bounded exponential backoff with jitter.
  Base delay: `100 × 2^attempt` ms. Jitter: random between 50%–100% of base.
  Capped at 300 seconds.
- **Rate-limit (429):** Uses the exact `Retry-After` header value in seconds.
  No jitter, no backoff. Missing, invalid, zero, or excessive (>300s) values
  cause the error to be thrown immediately.

### Cancellation

Cancellation is not directly supported in synchronous Python. Set a short
`timeout_ms` to limit request duration.

## Idempotency

```python
email = client.emails.send(
    from_="Acme <hello@acme.com>",
    to=["person@example.com"],
    subject="Your invoice",
    html="<p>Invoice attached</p>",
    idempotency_key="my-unique-key-abc123",
)
if email.duplicate:
    print("This send was a duplicate — the original was not re-attempted.")
```

## Emails

All email operations are on `client.emails`.

### Send an Email

```python
email = client.emails.send(
    from_="Acme <hello@acme.com>",
    to=["person@example.com", "Jane <jane@example.com>"],
    subject="Welcome",
    html="<h1>Welcome!</h1><p>Thanks for signing up.</p>",
    text="Welcome! Thanks for signing up.",
    type_="transactional",
    event_name="user.created",
    email_topic_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
    reply_to=["support@acme.com"],
    cc=["manager@acme.com"],
    bcc=["archive@acme.com"],
    headers={"X-Custom-Header": "value"},
)

print(email.id, email.status)
print(email.emails)           # list of recipient addresses
print(email.restricted_emails)  # list of suppressed addresses
print(email.duplicate)         # bool
```

### Send with a Template

```python
email = client.emails.send_with_template(
    from_="Acme <hello@acme.com>",
    to=["person@example.com"],
    template_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
    subject="Your order confirmation",
    template_variables=[
        {"key": "USER_NAME", "type": "string", "value": "John"},
        {"key": "ORDER_NUMBER", "type": "number", "value": 12345},
    ],
)
```

### Template Variables

Template variables can be passed as lists of dictionaries with `key`, `type`,
and `value` fields, as shown above.

### Attachments

```python
from letmesendemail import SendAttachment

email = client.emails.send(
    from_="Acme <hello@acme.com>",
    to=["person@example.com"],
    subject="With attachment",
    attachments=[
        # By URL
        {"name": "report.pdf", "path": "https://storage.example.com/report.pdf"},
        # By Base64 content
        {
            "name": "data.txt",
            "content": "c29tZSBmaWxlIGNvbnRlbnQ=",
        },
        # Inline with Content-ID
        {
            "name": "logo.png",
            "content": base64.b64encode(open("static/logo.png", "rb").read()).decode(),
            "content_id": "logo_cid",
            "content_disposition": "inline",
        },
    ],
)
```

**Attachment fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Filename shown to recipients (required) |
| `path` | str | Public URL where the file is hosted |
| `content` | str | Base64-encoded file content |
| `mime` | str | MIME type (e.g. `application/pdf`) |
| `content_id` | str | Content-ID for inline embedding |
| `content_disposition` | str | `"attachment"` or `"inline"` |

`path` and `content` are mutually exclusive. Provide one or the other, not both.

### Verify an Email Address

```python
result = client.emails.verify("person@example.com")

print(result.status)         # "valid", "invalid", or "risky"
print(result.score)          # 0-100
print(result.has_mailbox)    # True/False
print(result.is_disposable)  # True/False
print(result.is_role_based)  # True/False
print(result.domain_exists)  # True/False
print(result.valid_syntax)   # True/False
```

### List Emails

```python
page = client.emails.list(per_page=20)

for item in page.data:
    subject = item.subject or "(no subject)"
    print(item.id, subject, item.status)

pagination = page.pagination
print(pagination.has_more)     # bool
print(pagination.total)        # int (approximate)
print(pagination.per_page)     # int

# Next page (safe for empty results)
if pagination.has_more and page.data:
    last_id = page.data[-1].id
    next_page = client.emails.list(per_page=20, after=last_id)

# Previous page
if page.data:
    first_id = page.data[0].id
    prev_page = client.emails.list(per_page=20, before=first_id)
```

**`EmailListItem` fields:** `id`, `status`, `subject`, `event_name`, `type`,
`created_at`, `sent_at`, `recipients_count`, `attachments_count`.

### Get a Single Email

```python
detail = client.emails.get("01kvv5dv472evp42a60sy4p7zx")

print(detail.status, detail.subject)
print(detail.recipients_count, detail.attachments_count)

# Typed recipient objects
for r in detail.recipients:
    print(r.email_address, r.status, r.open_count, r.click_count)
    print(r.bounce_type, r.bounce_reason, r.bounced_at)
    print(r.complaint_type, r.complained_at)
    print(r.is_suppressed, r.suppression_reason)
    print(r.delivered_at, r.sent_at)
    print(r.failed_at, r.error_message)

# Typed attachment objects
for a in detail.attachments:
    print(a.name, a.mime, a.size, a.download_url)
    print(a.content_id, a.content_disposition)
```

## Domains

All domain operations are on `client.domains`.

```python
# List
page = client.domains.list(per_page=20)
for d in page.data:
    print(d.domain_name, d.status)

if page.pagination.has_more and page.data:
    next_page = client.domains.list(per_page=20, after=page.data[-1].id)

# Get
domain = client.domains.get("01kvv5th65xzkwxe5avmdqbn4a")
print(domain.domain_name, domain.status)

# Verify
result = client.domains.verify("example.com")
print(result.status)
```

## Contacts

All contact operations are on `client.contacts`.

```python
# Create
created_contact = client.contacts.create(
    email="john@example.com",
    first_name="John",
    last_name="Doe",
    phone="+1234567890",
    is_globally_unsubscribed=False,
    categories=["01kvtsch6f6e7hz543mjyjnqsp"],
    email_topics=["01kvtsch6gjgtx89z84jn8zwqg"],
)
print(created_contact.id, created_contact.email, created_contact.first_name)

# List
page = client.contacts.list(per_page=10)
for c in page.data:
    print(c.email, c.first_name)

if page.pagination.has_more and page.data:
    next_page = client.contacts.list(per_page=10, after=page.data[-1].id)

# Get
fetched_contact = client.contacts.get("01kvtsch80sxnzw8cggwhh22x2")
print(fetched_contact.email, fetched_contact.first_name, fetched_contact.last_name)

# Update
updated = client.contacts.update(
    "01kvtsch98rxyxwaxwx2fbpsbp",
    first_name="Jane",
    last_name="Doe",
    is_globally_unsubscribed=False,
    sync_categories=True,
)
print(updated.id)

# Delete
result = client.contacts.delete("01kvtscham9bjdwftnxxa8at1k")
print(result.status, result.message)
```

## Contact Categories

All category operations are on `client.contact_categories`.

```python
# Create
created_category = client.contact_categories.create(name="VIP", slug="vip")
print(created_category.id, created_category.name, created_category.slug)

# List
page = client.contact_categories.list(per_page=20)
for c in page.data:
    print(c.name, c.slug)

if page.pagination.has_more and page.data:
    next_page = client.contact_categories.list(per_page=20, after=page.data[-1].id)

# Get
fetched_category = client.contact_categories.get("01kvtr2b9ztdvggdbrcjmm45nj")
print(fetched_category.name)

# Update
updated_category = client.contact_categories.update(
    "01kvtkq34gc5zqbxpyw90q4sk6",
    name="Premium",
    slug="premium",
)
print(updated_category.slug)

# Delete
result = client.contact_categories.delete("01kvtmr3evcs2brxp2vcztd102")
print(result.status)
```

## Email Topics

All topic operations are on `client.email_topics`.

```python
# Create
created_topic = client.email_topics.create(
    name="Product Updates",
    slug="product-updates",
    description="Emails for product updates",
    auto_subscribe=True,
    public=True,
    domain_id="01kvtsgfavkx5609jd3j2t6jr1",
)
print(created_topic.id, created_topic.name, created_topic.auto_subscribe)

# List
page = client.email_topics.list(per_page=20)
for t in page.data:
    print(t.name, t.description)

if page.pagination.has_more and page.data:
    next_page = client.email_topics.list(per_page=20, after=page.data[-1].id)

# Get
fetched_topic = client.email_topics.get("01kvtsgf9e96nnj98nxsac751r")
print(fetched_topic.name, fetched_topic.auto_subscribe)

# Update
updated_topic = client.email_topics.update(
    "01kvtsgfcbte0npnqkj8kep642",
    name="New Name",
    description="Updated description",
    public=True,
)
print(updated_topic.name)

# Delete
result = client.email_topics.delete("01kvtsgfdq4xw54vcvqw0ae68n")
print(result.status, result.message)
```

## Pagination

List endpoints return typed responses with a `pagination` attribute:

```python
page = client.emails.list(per_page=10)
pag = page.pagination
print(pag.has_more, pag.total, pag.per_page, pag.fetched)
```

### Cursor Rules

- Pass `after` to fetch the next page (use the last item's ID).
- Pass `before` to fetch the previous page (use the first item's ID).
- Never pass `after` and `before` together.
- The API does not expose `has_previous`. Applications should retain
  previously used cursors for Back/Previous navigation.
- Cursor pagination does not allow jumps to arbitrary page numbers.
- Always check `pag.has_more` before requesting the next page.
- Always check that `page.data` is non-empty before accessing `[0]` or `[-1]`.

```python
page = client.emails.list(per_page=20)

for item in page.data:
    print(item.id, item.subject)

# Safe next-page navigation
if page.pagination.has_more and page.data:
    next_page = client.emails.list(per_page=20, after=page.data[-1].id)

# Safe previous-page navigation
if page.data:
    prev_page = client.emails.list(per_page=20, before=page.data[0].id)
```

## Errors and Exceptions

All API errors raise subclasses of `LetMeSendEmailError`:

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `ValidationError` | 400, 413, 422 | Request validation failed |
| `AuthenticationError` | 401 | Invalid or missing API key |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ConflictError` | 409 | Resource conflict |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ApiError` | 500+ | Server error or malformed successful response |
| `NetworkError` | — | Connection failed |
| `TimeoutError` | — | Request timed out |
| `WebhookVerificationError` | — | Webhook verification failed |
| `WebhookSigningError` | — | Webhook secret could not be decoded |

### Error Metadata

Every `LetMeSendEmailError` provides:

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | str | Human-readable error description |
| `status_code` | int | HTTP status code |
| `api_code` | str | API error code (e.g. `domain_not_found`) |
| `validation_errors` | dict | Field-level validation errors |
| `request_id` | str | Request ID for debugging |
| `response_headers` | dict | Response headers (lowercase keys) |
| `raw_body` | str | Exact raw response body |

`RateLimitError` additionally provides:

| Attribute | Type | Description |
|-----------|------|-------------|
| `retry_after` | int | Seconds to wait before retrying |
| `limit` | int | Rate-limit quota |
| `remaining` | int | Remaining requests |
| `reset_at` | str | Reset timestamp |

### Error Handling Example

```python
from letmesendemail import (
    LetMeSendEmail,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    ApiError,
)

client = LetMeSendEmail(api_key="lms_live_...")

try:
    email = client.emails.send(from_="...", to=["..."], subject="Hi")
except ValidationError as e:
    print(e.validation_errors)
    print(e.request_id)
except AuthenticationError:
    print("Check your API key")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ApiError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Timeouts

The default timeout is 30 seconds (30000 ms). Configure via `timeout_ms`:

```python
client = LetMeSendEmail(api_key="...", timeout_ms=60_000)
```

When a request times out, a `TimeoutError` is raised.

## Webhooks

Webhook signature verification is built into the SDK.

```python
import os
from typing import Any

from letmesendemail import verify_webhook

def handle_webhook(raw_payload: str, incoming_headers: dict[str, str]) -> dict[str, Any]:
    """Verify the framework's unmodified request body and incoming headers."""
    webhook_secret = os.environ.get("LETMESENDEMAIL_WEBHOOK_SECRET")
    if not webhook_secret:
        raise RuntimeError("LETMESENDEMAIL_WEBHOOK_SECRET environment variable is not set.")

    return verify_webhook(
        payload=raw_payload,
        headers=incoming_headers,
        secret=webhook_secret,
    )
```

Pass the exact raw body text—before JSON parsing—and the incoming headers from
your framework. Handle `WebhookVerificationError` as an invalid request and
`WebhookSigningError` as a server configuration error. The returned dictionary
contains the verified payload; its application-specific fields depend on the
webhook payload delivered by the API.

### Verification Details

**Required headers:**

| Header | Description |
|--------|-------------|
| `webhook-id` | Unique webhook message identifier |
| `webhook-log-id` | Log identifier |
| `webhook-timestamp` | Unix timestamp (seconds, ASCII digits only) |
| `webhook-signature` | One or more space-separated versioned signatures (`v1,<base64>`) |

**Header resolution:** Headers are matched case-insensitively. Both
`webhook-id` and `HTTP_WEBHOOK_ID` (as passed by some server frameworks)
are accepted.

**Signing algorithm:**

1. Strip the optional `whsec_` prefix from the secret.
2. Base64-decode the secret with strict validation.
3. Compute `HMAC-SHA256` over the string:
   `<webhook-id>.<webhook-log-id>.<webhook-timestamp>.<raw-payload>`
4. Base64-encode the raw HMAC output.
5. Compare against each `v1,` entry in `webhook-signature` using
   fixed-time comparison.

**Timestamp validation:**

- Must be a string of ASCII digits only (positive integer).
- Default tolerance: 300 seconds (5 minutes) in both past and future directions.
- Negative tolerance raises `WebhookSigningError`.

**Payload validation:**

- Malformed JSON raises `WebhookVerificationError` ("not valid JSON").
- Valid JSON that is not an object (array, string, number, null) raises
  `WebhookVerificationError` ("must be a JSON object").

## Model Serialization and Database Storage

Every typed response model provides a `to_dict()` method that returns a plain
dictionary suitable for JSON encoding, database storage, caching, or logging.
Request attachments use the public `SendAttachment` `TypedDict`, so they are
already plain dictionaries and do not require conversion.

### Serialization Mechanism

The SDK uses Python dataclasses. The `to_dict()` method uses
`dataclasses.asdict()` to recursively convert the model and all nested
models into plain dictionaries.

```python
import json
from letmesendemail import LetMeSendEmail

client = LetMeSendEmail("lms_live_your_api_key")

email = client.emails.get("email_abc123")
data = email.to_dict()

# Standard JSON encoding
json_str = json.dumps(data, indent=2)

# Database storage via application code
def save_record(table: str, record: dict) -> None:
    # Application-owned database implementation
    ...

save_record("emails", data)
```

### Supported Models

Every public response model supports `to_dict()`:

- `SendEmailResponse`, `VerifyEmailResponse`
- `EmailListItem`, `EmailListResponse`
- `ShowEmailResponse`, `Recipient`, `EmailAttachment`
- `DomainItem`, `DomainListResponse`
- `ContactItem`, `ContactListResponse`, `ContactUpdateResponse`
- `ContactCategoryItem`, `ContactCategoryListResponse`
- `EmailTopicItem`, `EmailTopicListResponse`
- `PaginationInfo`, `StatusResponse`

The public `SendAttachment` request type can be passed directly to
`json.dumps()` or copied with `dict(attachment)`:

```python
from letmesendemail import SendAttachment

attachment: SendAttachment = {
    "name": "report.pdf",
    "content": "cGRmLWNvbnRlbnQ=",
    "mime": "application/pdf",
    "content_disposition": "attachment",
}

serialized_attachment = dict(attachment)
```

### Nested Conversion

Nested dataclass models are converted recursively:

```python
email = client.emails.get("email_abc123")
data = email.to_dict()

# Recipients is a list of dicts with snake_case keys
for recipient in data["recipients"]:
    print(recipient["email_address"], recipient["open_count"])

# Attachments is a list of dicts
for att in data["attachments"]:
    print(att["name"], att["size"], att["download_url"])
```

### List Responses

List responses include both the `data` array and `pagination` metadata:

```python
page = client.emails.list(per_page=10)
data = page.to_dict()

items = data["data"]
pagination = data["pagination"]
print(pagination["has_more"], pagination["total"])
```

### Field Naming

Field names use the SDK's snake_case convention matching the API response
format:

- `created_at`
- `email_address`
- `has_more`
- `open_count`
- `download_url`

### Behavior Notes

- Null optional fields are serialized as `None`.
- Boolean values are preserved as Python `bool` types.
- Numeric values are preserved as Python `int` types.
- String values including dates (ISO 8601) and identifiers are preserved as
  Python `str` types.
- Lists are preserved as Python `list`.
- Empty lists are serialized as `[]`.
- Dictionaries are preserved as Python `dict`.
- The returned dictionary is a copy; mutating it does not affect the source
  model.
- API keys, webhook secrets, HTTP clients, and internal SDK state are never
  included in the output.

## Testing

```bash
pip install -e ".[dev]"
pytest -v
```

### Code Quality

```bash
ruff check .
ruff format --check .
pyright
```

## Runtime Support

| Python | Supported |
|--------|-----------|
| 3.9 | Yes |
| 3.10 | Yes |
| 3.11 | Yes |
| 3.12 | Yes |
| 3.13 | Yes |
| 3.14 | Yes |

## Upgrading

### From 0.1.0 to 0.2.0

- Retry logic was rewritten for conservative, bounded exponential backoff
  with jitter. 429 responses without a valid `Retry-After` are now thrown
  immediately rather than retried.
- Webhook timestamp validation now requires ASCII digits only (positive
  integers). Decimal timestamps and negative values are rejected.
- Webhook payload validation distinguishes malformed JSON from valid
  non-object JSON (arrays, scalars).
- Malformed 2xx responses (null, arrays, scalars, invalid JSON) now raise
  `ApiError` preserving the status, headers, and raw body.

No migration guide is currently required for the current version. See the
[changelog](https://github.com/letmesendemail/letmesendemail-python/blob/master/CHANGELOG.md) for all changes.

## Getting Help

- [API Documentation](https://letmesend.email/docs)
- [GitHub Repository](https://github.com/letmesendemail/letmesendemail-python)
- [Issue Tracker](https://github.com/letmesendemail/letmesendemail-python/issues)
- [Changelog](https://github.com/letmesendemail/letmesendemail-python/blob/master/CHANGELOG.md)
