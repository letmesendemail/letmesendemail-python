"""Main client class for the letmesend.email SDK."""

from __future__ import annotations

import random
import time
from typing import Any

import httpx

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version

    _SDK_VERSION = _pkg_version("letmesendemail")
except (PackageNotFoundError, ImportError):
    _SDK_VERSION = "0.0.0"

from letmesendemail._config import MAX_RETRY_DELAY, ClientConfig
from letmesendemail._errors import (
    ApiError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    _error_from_response,
)
from letmesendemail.resources.contact_categories import ContactCategoriesResource
from letmesendemail.resources.contacts import ContactsResource
from letmesendemail.resources.domains import DomainsResource
from letmesendemail.resources.email_topics import EmailTopicsResource
from letmesendemail.resources.emails import EmailsResource

RETRYABLE_STATUSES = frozenset({408, 500, 502, 503, 504})

_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "DELETE"})


def _has_idempotency_key(extra_headers: dict[str, str] | None) -> bool:
    if not extra_headers:
        return False
    return any(k.lower() == "idempotency-key" for k in extra_headers)


def _jitter(base_ms: int) -> float:
    return (base_ms * (0.5 + random.random() * 0.5)) / 1000.0


class LetMeSendEmail:
    """Main SDK client for letmesend.email."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout_ms: int | None = None,
        retries: int | None = None,
        _client: httpx.Client | None = None,
    ) -> None:
        if api_key is None:
            raise ValueError("api_key is required")
        self._config = ClientConfig(
            api_key=api_key,
            base_url=base_url or ClientConfig.base_url,
            timeout_ms=timeout_ms or ClientConfig.timeout_ms,
            retries=retries or ClientConfig.retries,
        )
        self._owns_client = _client is None
        self._http = _client or httpx.Client(
            timeout=httpx.Timeout(self._config.timeout_ms / 1000),
        )

    def close(self) -> None:
        """Close the underlying HTTP client if owned."""
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> LetMeSendEmail:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with optional retries."""
        url = f"{self._config.base_url}/{path.lstrip('/')}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"letmesendemail-python/{_SDK_VERSION}",
        }
        if extra_headers:
            headers.update(extra_headers)

        may_retry = self._config.retries > 0 and (
            method in _IDEMPOTENT_METHODS or _has_idempotency_key(extra_headers)
        )
        max_attempts = (self._config.retries + 1) if may_retry else 1

        last_error: Exception | None = None

        for attempt in range(max_attempts):
            try:
                return self._send(method, url, body, headers)
            except (NetworkError, TimeoutError) as exc:
                if not may_retry or attempt == max_attempts - 1:
                    raise
                last_error = exc
                delay = min(_jitter(100 * (2**attempt)), MAX_RETRY_DELAY)
                time.sleep(delay)
            except Exception as exc:
                if isinstance(exc, RateLimitError):
                    if not may_retry or attempt == max_attempts - 1:
                        raise
                    retry_after = exc.retry_after
                    if retry_after is None or retry_after <= 0:
                        raise
                    if retry_after > MAX_RETRY_DELAY:
                        raise
                    time.sleep(retry_after)
                    last_error = exc
                elif isinstance(exc, ApiError):
                    if (
                        not may_retry
                        or attempt == max_attempts - 1
                        or (exc.status_code and exc.status_code not in RETRYABLE_STATUSES)
                    ):
                        raise
                    last_error = exc
                    delay = min(_jitter(100 * (2**attempt)), MAX_RETRY_DELAY)
                    time.sleep(delay)
                else:
                    raise

        raise last_error  # type: ignore[misc]

    def _send(
        self,
        method: str,
        url: str,
        body: dict[str, Any] | None,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Send a single HTTP request without retries."""
        try:
            response = self._http.request(method, url, json=body, headers=headers)
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timed out.") from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

        response_headers: dict[str, str] = {}
        for key, val in response.headers.items():
            response_headers[key.lower()] = val

        raw_text = response.text

        try:
            parsed: Any = response.json()
        except Exception:
            parsed = None

        if response.status_code >= 400:
            body_map: dict[str, Any] = {}
            if isinstance(parsed, dict):
                body_map = parsed
            raise _error_from_response(response.status_code, body_map, response_headers, raw_text)

        # Reject malformed 2xx responses (non-object, arrays, null)
        if not isinstance(parsed, dict):
            raise ApiError(
                "Malformed response body",
                response.status_code,
                response_headers=response_headers,
                raw_body=raw_text,
            )

        return parsed

    @property
    def emails(self) -> EmailsResource:
        """Access the Emails resource."""
        return EmailsResource(self._request)

    @property
    def domains(self) -> DomainsResource:
        """Access the Domains resource."""
        return DomainsResource(self._request)

    @property
    def contacts(self) -> ContactsResource:
        """Access the Contacts resource."""
        return ContactsResource(self._request)

    @property
    def contact_categories(self) -> ContactCategoriesResource:
        """Access the Contact Categories resource."""
        return ContactCategoriesResource(self._request)

    @property
    def email_topics(self) -> EmailTopicsResource:
        """Access the Email Topics resource."""
        return EmailTopicsResource(self._request)
