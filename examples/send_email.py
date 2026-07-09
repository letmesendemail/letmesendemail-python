"""Example: send an email using the letmesend.email Python SDK."""

import os

from letmesendemail import LetMeSendEmail

client = LetMeSendEmail(api_key=os.environ.get("LETMESENDEMAIL_API_KEY", "lms_live_..."))

try:
    email = client.emails.send(
        from_="Acme <hello@acme.com>",
        to=["person@example.com"],
        subject="Hello from letmesend.email",
        html="<p>Hello from letmesend.email</p>",
        type_="transactional",
    )
    print(f"Email sent! ID: {email.id}, Status: {email.status}")
except Exception as e:
    print(f"Error: {e}")
