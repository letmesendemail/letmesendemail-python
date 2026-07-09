from __future__ import annotations

from typing import Any


class LetMeSendEmailError(Exception):
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


class ApiError(LetMeSendEmailError): ...


class AuthenticationError(LetMeSendEmailError): ...


class AuthorizationError(LetMeSendEmailError): ...


class ValidationError(LetMeSendEmailError): ...


class RateLimitError(LetMeSendEmailError):
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


class NotFoundError(LetMeSendEmailError): ...


class ConflictError(LetMeSendEmailError): ...


class NetworkError(LetMeSendEmailError): ...


class TimeoutError(LetMeSendEmailError): ...


class WebhookVerificationError(LetMeSendEmailError): ...


class WebhookSigningError(LetMeSendEmailError): ...


def _error_from_response(
    status: int,
    body: dict[str, Any],
    headers: dict[str, str],
) -> LetMeSendEmailError:
    message = body.get("message", "Unknown error.")
    api_code = body.get("name")
    validation_errors = body.get("errors")
    raw_body_str = str(body)
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
        retry_after = _parse_int_header(headers, "retry-after")
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


def _parse_int_header(headers: dict[str, str], name: str) -> int | None:
    val = headers.get(name)
    if val is not None:
        try:
            return int(val)
        except (ValueError, TypeError):
            return None
    return None
