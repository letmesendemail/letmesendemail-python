# letmesend.email Python SDK

The official Python SDK for the [letmesend.email](https://letmesend.email/) API.

## Installation

```bash
pip install letmesendemail
```

Requires Python 3.9 or later.

## Quick Start

```python
from letmesendemail import LetMeSendEmail

client = LetMeSendEmail(api_key="lms_live_...")

email = client.emails.send(
    from_="Acme <hello@acme.com>",
    to=["person@example.com"],
    subject="Welcome",
    html="<p>Hello from letmesend.email</p>",
)
print(email.id, email.status)
```

## Configuration

```python
client = LetMeSendEmail(
    api_key="lms_live_...",
    base_url="https://letmesend.email/api/v1",
    timeout_ms=30_000,
    retries=0,
)
```

### WithRetry Semantics

When `retries > 0`, the SDK automatically retries on:

- **Network errors** (connection refused, DNS failure)
- **Timeouts**
- **HTTP 408, 500, 502, 503, 504**
- **HTTP 429** — only when `Retry-After` header is present, valid (positive integer ≤ 300s)

Retries use **bounded exponential backoff with jitter**:

- Base delay = `100 × 2^attempt` milliseconds
- Actual delay = `base × (0.5 + random × 0.5)` clamped to `[0, 300]` seconds
- Network errors and timeouts use jittered backoff
- 429 uses the exact `Retry-After` value (no jitter, capped at 300s)

Non-idempotent methods (`POST`, `PUT`, `PATCH`) are **not retried** unless an
`Idempotency-Key` header is provided.

Safe methods (`GET`, `HEAD`, `OPTIONS`, `DELETE`) are always retried.

### IdempotencyKey

```python
email = client.emails.send(
    from_="...",
    to=["..."],
    subject="Hi",
    idempotency_key="my-unique-key",
)
```

When an `Idempotency-Key` is provided on a `POST`, the request becomes eligible
for retries. The same idempotency key can be sent multiple times and the API
will only process it once.

## Resources

### Emails

#### Send

```python
email = client.emails.send(
    from_="Acme <hello@acme.com>",
    to=["user@example.com"],
    subject="Welcome",
    html="<p>Hello</p>",
    text="Hello",                     # optional plain text
    type_="transactional",            # optional
    event_name="welcome",             # optional
    email_topic_id="topic_1",         # optional
    reply_to=["support@acme.com"],    # optional
    cc=["cc@example.com"],            # optional
    bcc=["bcc@example.com"],          # optional
    headers={"X-Custom": "value"},    # optional
    idempotency_key="my-key",         # optional
)
print(email.id, email.status)
```

**Attachments** — by URL:

```python
from letmesendemail import SendAttachment

email = client.emails.send(
    from_="...",
    to=["..."],
    subject="With attachment",
    attachments=[
        {"name": "report.pdf", "path": "https://storage.example.com/report.pdf"},
    ],
)
```

**Attachments** — by base64 content:

```python
email = client.emails.send(
    from_="...",
    to=["..."],
    subject="With inline image",
    attachments=[
        {
            "name": "logo.png",
            "content": "iVBORw0KGgo...",
            "content_id": "logo_cid",
            "content_disposition": "inline",
        },
    ],
)
```

#### Send with Template

```python
email = client.emails.send_with_template(
    from_="...",
    to=["..."],
    template_id="tpl_1",
    template_variables=[{"key": "name", "value": "Alice"}],
)
```

#### Verify

```python
result = client.emails.verify("person@example.com")
print(result.status, result.score)
# "valid", 95
```

#### List (Cursor Pagination)

```python
page = client.emails.list(per_page=20)
for item in page.data:
    print(item.id, item.subject, item.status)

print(page.pagination.has_more)

# Next page
if page.pagination.has_more:
    next_page = client.emails.list(
        per_page=20,
        after=page.data[-1].id,
    )
```

#### Get

```python
detail = client.emails.get("email_id")
print(detail.status, detail.recipients_count)
for r in detail.recipients:
    print(r.email_address, r.status, r.open_count)
```

### Domains

```python
# List
domains = client.domains.list()
for d in domains.data:
    print(d.domain_name, d.status)

# Get
domain = client.domains.get("domain_id")

# Verify
result = client.domains.verify("example.com")
print(result.status)
```

### Contacts

```python
# Create
contact = client.contacts.create(
    email="user@example.com",
    first_name="John",
    last_name="Doe",
    phone="+1234567890",
    categories=["cat_id_1"],
    email_topics=["topic_id_1"],
)

# List
page = client.contacts.list(per_page=20, after="cursor")

# Get
contact = client.contacts.get("contact_id")

# Update
result = client.contacts.update(
    "contact_id",
    first_name="Jane",
    sync_categories=True,
)

# Delete
result = client.contacts.delete("contact_id")
print(result.status)
```

### Contact Categories

```python
# Create
cat = client.contact_categories.create("Newsletter", slug="newsletter")

# List
page = client.contact_categories.list()

# Get
cat = client.contact_categories.get("category_id")

# Update
cat = client.contact_categories.update("category_id", "Updates", slug="updates")

# Delete
result = client.contact_categories.delete("category_id")
```

### Email Topics

```python
# Create
topic = client.email_topics.create(
    "Product Update",
    "product-update",
    auto_subscribe=True,
    public=True,
    domain_id="domain_id",
)

# List
page = client.email_topics.list()

# Get
topic = client.email_topics.get("topic_id")

# Update
topic = client.email_topics.update(
    "topic_id",
    name="Renamed",
    slug="renamed",
    public=True,
)

# Delete
result = client.email_topics.delete("topic_id")
```

### Pagination

List responses return a `data` list and a `pagination` object:

```python
page = client.emails.list(per_page=20, after="cursor_id")

page.pagination.has_more   # bool — more results available
page.pagination.per_page   # int — items per page
page.pagination.total      # int — total items (may be approximate)
page.pagination.fetched    # int — items in this response
```

Cursor-based pagination uses `after` (forward) and `before` (backward) cursors.

## Error Handling

Every error is a subclass of `LetMeSendEmailError`:

| Exception | HTTP Status | When |
|---|---|---|
| `ValidationError` | 400, 413, 422 | Request validation failed |
| `AuthenticationError` | 401 | Invalid or missing API key |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ConflictError` | 409 | Resource conflict |
| `RateLimitError` | 429 | Too many requests |
| `ApiError` | 5xx+ | Server-side error |
| `NetworkError` | — | Connection refused, DNS failure |
| `TimeoutError` | — | Request timed out |

```python
from letmesendemail import RateLimitError, ValidationError, AuthenticationError, ApiError

try:
    client.emails.send(...)
except ValidationError as e:
    print(e.validation_errors)    # dict of field → [messages]
    print(e.api_code)             # "validation_error"
    print(e.request_id)           # "req_..."
    print(e.raw_body)             # raw response text
    print(e.response_headers)     # lowercase headers dict
except AuthenticationError:
    print("Check API key")
except RateLimitError as e:
    print(f"Retry after {e.retry_after}s")
except ApiError as e:
    print(f"Error {e.status_code}: {e.message}")
```

## Webhooks

```python
from letmesendemail import verify_webhook

event = verify_webhook(
    payload=raw_body,          # raw request body as string
    headers=incoming_headers,  # dict (case-insensitive, HTTP_ prefix supported)
    secret="whsec_...",        # base64-encoded or whsec_-prefixed secret
)
print(event)
```

The verification function:

- Validates all four required headers (`webhook-id`, `webhook-log-id`,
  `webhook-timestamp`, `webhook-signature`)
- Checks timestamp is within a 300-second tolerance (customizable via `tolerance`)
- Computes HMAC-SHA256 over `id.log.timestamp.payload`
- Accepts any matching `v1,` signature entry
- Parses payload as JSON and returns the parsed dict

```python
event = verify_webhook(
    payload=raw_body,
    headers=incoming_headers,
    secret="whsec_base64secret",
    tolerance=60,  # 60-second window
)
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

The SDK does not include a `Mail::fake()` equivalent. For integration testing,
use `httpx_mock` via the `pytest-httpx` fixture:

```python
def test_send_email(httpx_mock):
    from letmesendemail import LetMeSendEmail

    client = LetMeSendEmail(api_key="test", base_url="https://letmesend.email/api/v1")
    httpx_mock.add_response(
        method="POST",
        url="https://letmesend.email/api/v1/emails",
        json={"id": "...", "status": "accepted"},
    )
    email = client.emails.send(from_="...", to=["..."], subject="Hi")
    assert email.status == "accepted"
```

## Version Support

| Python | Supported |
|--------|-----------|
| 3.9 | Yes |
| 3.10 | Yes |
| 3.11 | Yes |
| 3.12 | Yes |
| 3.13 | Yes |
| 3.14 | Yes |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
