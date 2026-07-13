"""Example: send an email using the letmesend.email Python SDK."""

import os

from letmesendemail import LetMeSendEmail, LetMeSendEmailError

api_key = os.environ.get("LETMESENDEMAIL_API_KEY")
if not api_key:
    raise RuntimeError("LETMESENDEMAIL_API_KEY environment variable is required")

try:
    with LetMeSendEmail(api_key=api_key) as client:
        email = client.emails.send(
            from_="Acme <hello@acme.com>",
            to=["person@example.com"],
            subject="Hello from letmesend.email",
            html="<p>Hello from letmesend.email</p>",
            type_="transactional",
        )
    print(f"Email sent! ID: {email.id}, Status: {email.status}")
except LetMeSendEmailError as exc:
    raise SystemExit(f"Request failed: {exc}") from exc
