"""letmesend.email Python SDK."""

from letmesendemail._client import LetMeSendEmail
from letmesendemail._errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    LetMeSendEmailError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    WebhookSigningError,
    WebhookVerificationError,
)
from letmesendemail._models import ContactUpdateResponse, SendAttachment
from letmesendemail.webhooks import verify_webhook

__all__ = [
    "LetMeSendEmail",
    "LetMeSendEmailError",
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    "WebhookVerificationError",
    "WebhookSigningError",
    "ContactUpdateResponse",
    "SendAttachment",
    "verify_webhook",
]
