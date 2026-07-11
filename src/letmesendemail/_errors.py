"""Structured error classes for the SDK."""

from __future__ import annotations

import calendar
import time
from typing import Any


class LetMeSendEmailError(Exception):
    """Base error for all SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        api_code: str | None = None,
        validation_errors: dict[str, list[str]] | None = None,
        request_id: str | None = None,
        response_headers: dict[str, str] | None = None,
        raw_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.api_code = api_code
        self.validation_errors = validation_errors or {}
        self.request_id = request_id
        self.response_headers = response_headers or {}
        self.raw_body = raw_body


class ApiError(LetMeSendEmailError):
    """Server-side API error (5xx or unhandled status)."""


class AuthenticationError(LetMeSendEmailError):
    """401 Unauthorized — invalid or missing API key."""


class AuthorizationError(LetMeSendEmailError):
    """403 Forbidden — insufficient permissions."""


class ValidationError(LetMeSendEmailError):
    """400, 413, or 422 — request validation failed."""


class RateLimitError(LetMeSendEmailError):
    """429 Too Many Requests."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        api_code: str | None = None,
        validation_errors: dict[str, list[str]] | None = None,
        request_id: str | None = None,
        response_headers: dict[str, str] | None = None,
        raw_body: str | None = None,
        retry_after: int | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset_at: str | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code,
            api_code,
            validation_errors,
            request_id,
            response_headers,
            raw_body,
        )
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at


class NotFoundError(LetMeSendEmailError):
    """404 Not Found."""


class ConflictError(LetMeSendEmailError):
    """409 Conflict."""


class NetworkError(LetMeSendEmailError):
    """Transport-level failure (no HTTP response)."""


class TimeoutError(LetMeSendEmailError):
    """Request timed out."""


class WebhookVerificationError(LetMeSendEmailError):
    """Webhook signature verification failed."""


class WebhookSigningError(LetMeSendEmailError):
    """Webhook signing secret could not be decoded."""


def _parse_retry_after(headers: dict[str, str]) -> int | None:
    raw = headers.get("retry-after")
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        pass
    try:
        parsed = calendar.timegm(time.strptime(raw, "%a, %d %b %Y %H:%M:%S %Z"))
        delay = parsed - int(time.time())
        return delay if delay > 0 else None
    except (ValueError, TypeError):
        return None


def _parse_int_header(headers: dict[str, str], name: str) -> int | None:
    val = headers.get(name)
    if val is not None:
        try:
            return int(val)
        except (ValueError, TypeError):
            return None
    return None


def _error_from_response(
    status: int,
    body: dict[str, Any],
    headers: dict[str, str],
    raw_text: str | None = None,
) -> LetMeSendEmailError:
    """Map an HTTP status code and response body to a typed error."""
    message = body.get("message", "Unknown error.")
    api_code = body.get("name")
    validation_errors = body.get("errors")
    raw_body_str = raw_text or str(body)
    request_id = headers.get("x-request-id")

    kwargs: dict[str, Any] = {
        "message": message,
        "status_code": status,
        "api_code": api_code,
        "validation_errors": validation_errors,
        "request_id": request_id,
        "response_headers": headers,
        "raw_body": raw_body_str,
    }

    if status in (400, 413, 422):
        return ValidationError(**kwargs)
    if status == 401:
        return AuthenticationError(**kwargs)
    if status == 403:
        return AuthorizationError(**kwargs)
    if status == 404:
        return NotFoundError(**kwargs)
    if status == 409:
        return ConflictError(**kwargs)
    if status == 429:
        retry_after = _parse_retry_after(headers)
        limit = _parse_int_header(headers, "x-ratelimit-limit")
        remaining = _parse_int_header(headers, "x-ratelimit-remaining")
        reset_at = headers.get("x-ratelimit-reset")
        return RateLimitError(
            **kwargs,
            retry_after=retry_after,
            limit=limit,
            remaining=remaining,
            reset_at=reset_at,
        )
    if status >= 500:
        return ApiError(**kwargs)
    return ApiError(**kwargs)
