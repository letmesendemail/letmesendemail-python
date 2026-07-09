# letmesend.email Python SDK

The official Python SDK for the [letmesend.email](https://letmesend.email/) API.

## Installation

```bash
pip install letmesendemail
```

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
# With full configuration
client = LetMeSendEmail(
    api_key="lms_live_...",
    base_url="https://letmesend.email/api/v1",
    timeout_ms=30_000,
    retries=0,
)
```

## Resources

### Emails

```python
# Send
email = client.emails.send(from_="...", to=["..."], subject="Hi", html="<p>Hi</p>")

# Send with template
email = client.emails.send_with_template(
    from_="...", to=["..."], template_id="...", template_variables=[...]
)

# Verify
result = client.emails.verify("person@example.com")
print(result.status, result.score)

# List
page = client.emails.list(per_page=20)
for item in page.data:
    print(item.id, item.subject)
print(page.pagination.has_more)

# Get
detail = client.emails.get("id")
print(detail.status, detail.recipients_count)
```

### Domains, Contacts, Contact Categories, Email Topics

See source code or the full [README on GitHub](https://github.com/letmesendemail/letmesendemail-python).

## Webhooks

```python
from letmesendemail import verify_webhook

event = verify_webhook(
    payload=raw_body,
    headers=incoming_headers,
    secret="whsec_...",
)
print(event)
```

## Error Handling

```python
from letmesendemail import ValidationError, AuthenticationError, ApiError

try:
    client.emails.send(...)
except ValidationError as e:
    print(e.validation_errors)
except AuthenticationError:
    print("Check API key")
except ApiError as e:
    print(f"Error {e.status_code}: {e.message}")
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## Version Support

| Python | Supported |
|--------|-----------|
| 3.10 | Yes |
| 3.11 | Yes |
| 3.12 | Yes |
| 3.13 | Yes |
| 3.14 | Yes |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
