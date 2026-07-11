"""Tests for the main SDK client — config, requests, retries, errors, malformed."""

from __future__ import annotations

import importlib.metadata
import json
from typing import Any
from unittest.mock import call, patch

import httpx
import pytest

from letmesendemail import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from letmesendemail._client import LetMeSendEmail

SEND_FIXTURE = {
    "id": "01kvv5a6xk9qd6y2egeae8w76e",
    "status": "accepted",
    "emails": ["john@example.com"],
    "restricted_emails": [],
}

_EMAIL_URL = "https://letmesend.email/api/v1/emails"


def _mock_send(httpx_mock: Any) -> None:
    httpx_mock.add_response(method="POST", url=_EMAIL_URL, json=SEND_FIXTURE)


@pytest.fixture
def client() -> LetMeSendEmail:
    return LetMeSendEmail(api_key="test_key", base_url="https://letmesend.email/api/v1")


# ── Config ──


def test_default_config() -> None:
    c = LetMeSendEmail(api_key="test")
    assert c._config.base_url == "https://letmesend.email/api/v1"
    assert c._config.timeout_ms == 30_000
    assert c._config.retries == 0


def test_custom_config() -> None:
    c = LetMeSendEmail(api_key="test", base_url="https://custom.test", timeout_ms=10_000, retries=3)
    assert c._config.base_url == "https://custom.test"
    assert c._config.timeout_ms == 10_000
    assert c._config.retries == 3


# ── Request recording ──


def test_user_agent_contains_version(client: LetMeSendEmail, httpx_mock: Any) -> None:
    _mock_send(httpx_mock)

    client.emails.send(from_="a@b.com", to=["c@d.com"], subject="Hi")

    req = httpx_mock.get_request()
    ua = req.headers["User-Agent"]
    assert ua.startswith("letmesendemail-python/")
    assert len(ua) > len("letmesendemail-python/")


def test_user_agent_exact_version(client: LetMeSendEmail, httpx_mock: Any) -> None:
    _mock_send(httpx_mock)

    client.emails.send(from_="a@b.com", to=["c@d.com"], subject="Hi")

    req = httpx_mock.get_request()
    version = importlib.metadata.version("letmesendemail")
    assert req.headers["User-Agent"] == f"letmesendemail-python/{version}"


def test_records_method_url_auth_headers_body(client: LetMeSendEmail, httpx_mock: Any) -> None:
    _mock_send(httpx_mock)

    client.emails.send(from_="a@b.com", to=["c@d.com"], subject="Hi", html="<p>Hi</p>")

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/emails")
    assert req.headers["Authorization"] == "Bearer test_key"
    assert req.headers["Content-Type"] == "application/json"
    assert req.headers["Accept"] == "application/json"

    body = json.loads(req.content)
    assert body["from"] == "a@b.com"
    assert body["to"] == ["c@d.com"]
    assert body["subject"] == "Hi"
    assert body["html"] == "<p>Hi</p>"


def test_attachment_serialization(client: LetMeSendEmail, httpx_mock: Any) -> None:
    _mock_send(httpx_mock)

    client.emails.send(
        from_="a@b.com",
        to=["c@d.com"],
        subject="Hi",
        attachments=[
            {"name": "f.pdf", "path": "https://ex.com/f.pdf"},
            {"name": "d.txt", "content": "aGVsbG8="},
            {
                "name": "i.png",
                "content": "aW1hZ2U=",
                "content_id": "cid123",
                "content_disposition": "inline",
            },
        ],
    )

    body = json.loads(httpx_mock.get_request().content)
    atts = body["attachments"]
    assert atts[0]["path"] == "https://ex.com/f.pdf"
    assert atts[1]["content"] == "aGVsbG8="
    assert atts[2]["content_id"] == "cid123"
    assert atts[2]["content_disposition"] == "inline"


# ── Idempotency ──


def test_idempotency_key_passed_as_header(client: LetMeSendEmail, httpx_mock: Any) -> None:
    _mock_send(httpx_mock)

    client.emails.send(from_="a@b.com", to=["c@d.com"], subject="Hi", idempotency_key="my-key")

    assert httpx_mock.get_request().headers["Idempotency-Key"] == "my-key"


# ── Errors ──


def test_error_exposes_raw_body_and_headers(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=_EMAIL_URL,
        status_code=422,
        json={"message": "Invalid", "name": "validation_error", "errors": {"email": ["Required"]}},
        headers={"x-request-id": "req_123"},
    )

    with pytest.raises(ValidationError) as exc:
        client.emails.send(from_="", to=[], subject="")  # type: ignore[arg-type]

    err = exc.value
    assert err.api_code == "validation_error"
    assert err.validation_errors == {"email": ["Required"]}
    assert err.request_id == "req_123"


def test_error_exposes_raw_body_text(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=_EMAIL_URL,
        status_code=422,
        json={"message": "Invalid", "name": "validation_error", "errors": {"email": ["Required"]}},
    )

    with pytest.raises(ValidationError) as exc:
        client.emails.send(from_="", to=[], subject="")

    err = exc.value
    assert err.raw_body is not None
    assert "Invalid" in err.raw_body
    assert "Required" in err.raw_body


def test_error_response_headers_preserved(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=_EMAIL_URL,
        status_code=422,
        json={"message": "Bad", "name": "validation_error"},
        headers={"X-Request-Id": "req_123", "X-Custom-Header": "custom_val"},
    )

    with pytest.raises(ValidationError) as exc:
        client.emails.send(from_="", to=[], subject="")

    err = exc.value
    assert err.response_headers.get("x-request-id") == "req_123"
    assert err.response_headers.get("x-custom-header") == "custom_val"


def test_validation_errors(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=_EMAIL_URL,
        status_code=422,
        json={
            "message": "Validation failed",
            "name": "validation_error",
            "errors": {"email": ["The email field is required."]},
        },
    )

    with pytest.raises(ValidationError) as exc:
        client.emails.send(from_="", to=[], subject="")

    err = exc.value
    assert err.validation_errors == {"email": ["The email field is required."]}


def test_timeout_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_exception(httpx.TimeoutException("timed out"))

    with pytest.raises(TimeoutError):
        client._request("GET", "/test")


def test_network_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_exception(httpx.ConnectError("refused"))

    with pytest.raises(NetworkError):
        client._request("GET", "/test")


# ── Malformed 2xx ──


def test_malformed_null_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET", url="https://letmesend.email/api/v1/emails", status_code=200, text="null"
    )

    with pytest.raises(ApiError) as exc:
        client._request("GET", "/emails")
    assert exc.value.status_code == 200


def test_malformed_array_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/emails",
        status_code=200,
        text='[{"id":"e1"}]',
    )

    with pytest.raises(ApiError) as exc:
        client._request("GET", "/emails")
    assert exc.value.status_code == 200


def test_malformed_invalid_json(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET", url="https://letmesend.email/api/v1/emails", status_code=200, text="not-json"
    )

    with pytest.raises(ApiError) as exc:
        client._request("GET", "/emails")
    assert exc.value.raw_body == "not-json"


# ── Retries (sequential responses) ──


def _make_sequential_mock(httpx_mock: Any, url: str, method: str, responses: list[dict]) -> None:
    """Add responses in sequence via callback."""
    call_count: list[int] = [0]

    def callback(request: httpx.Request) -> httpx.Response:
        idx = call_count[0]
        call_count[0] += 1
        resp_data = responses[idx] if idx < len(responses) else {"json": {}}
        if "error" in resp_data:
            raise resp_data["error"]
        return httpx.Response(
            status_code=resp_data.get("status", 200),
            json=resp_data.get("json"),
            headers=resp_data.get("headers", {}),
        )

    httpx_mock.add_callback(callback, method=method, url=url, is_reusable=True)


def test_retry_network_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 2
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {"error": httpx.ConnectError("e1")},
            {"error": httpx.ConnectError("e2")},
            {"json": {}},
        ],
    )

    with (
        patch("letmesendemail._client.time.sleep") as mock_sleep,
        patch("letmesendemail._client.random.random", return_value=0.5),
    ):
        result = client._request("GET", "/test")

    assert result == {}
    assert mock_sleep.call_count == 2
    mock_sleep.assert_has_calls([call(0.075), call(0.15)])


def test_retry_429_with_retry_after(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {
                "status": 429,
                "json": {"name": "rate_limited", "message": "Too fast"},
                "headers": {"Retry-After": "5"},
            },
            {"json": {}},
        ],
    )

    with patch("letmesendemail._client.time.sleep") as mock_sleep:
        result = client._request("GET", "/test")

    assert result == {}
    mock_sleep.assert_called_once_with(5.0)


def test_retry_429_excessive(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {
                "status": 429,
                "json": {"name": "rate_limited", "message": "Too fast"},
                "headers": {"Retry-After": "301"},
            },
        ],
    )

    with patch("letmesendemail._client.time.sleep") as mock_sleep:
        with pytest.raises(RateLimitError):
            client._request("GET", "/test")

    mock_sleep.assert_not_called()


def test_retry_429_zero(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {
                "status": 429,
                "json": {"name": "rate_limited", "message": "Too fast"},
                "headers": {"Retry-After": "0"},
            },
        ],
    )

    with patch("letmesendemail._client.time.sleep") as mock_sleep:
        with pytest.raises(RateLimitError):
            client._request("GET", "/test")

    mock_sleep.assert_not_called()


def test_retry_429_missing(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {"status": 429, "json": {"name": "rate_limited", "message": "Too fast"}},
        ],
    )

    with patch("letmesendemail._client.time.sleep") as mock_sleep:
        with pytest.raises(RateLimitError):
            client._request("GET", "/test")

    mock_sleep.assert_not_called()


def test_retry_500(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {"status": 500, "json": {"name": "error", "message": "E"}},
            {"json": {}},
        ],
    )

    with (
        patch("letmesendemail._client.time.sleep") as mock_sleep,
        patch("letmesendemail._client.random.random", return_value=0.5),
    ):
        result = client._request("GET", "/test")

    assert result == {}
    mock_sleep.assert_called_once_with(0.075)


def test_exhaust_retries(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "GET",
        [
            {"status": 500, "json": {"name": "error", "message": "E"}},
            {"status": 500, "json": {"name": "error", "message": "E"}},
        ],
    )

    with (
        patch("letmesendemail._client.time.sleep") as mock_sleep,
        patch("letmesendemail._client.random.random", return_value=0.5),
    ):
        with pytest.raises(ApiError):
            client._request("GET", "/test")

    mock_sleep.assert_called_once_with(0.075)


def test_no_retry_non_idempotent_post(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 2
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "POST",
        [
            {"status": 500, "json": {"name": "error", "message": "E"}},
        ],
    )

    with patch("letmesendemail._client.time.sleep") as mock_sleep:
        with pytest.raises(ApiError):
            client._request("POST", "/test", {})

    mock_sleep.assert_not_called()


def test_retry_idempotent_post_with_key(client: LetMeSendEmail, httpx_mock: Any) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        "POST",
        [
            {"status": 500, "json": {"name": "error", "message": "E"}},
            {"json": {}},
        ],
    )

    with (
        patch("letmesendemail._client.time.sleep") as mock_sleep,
        patch("letmesendemail._client.random.random", return_value=0.5),
    ):
        result = client._request("POST", "/test", {}, {"Idempotency-Key": "k"})

    assert result == {}
    mock_sleep.assert_called_once_with(0.075)


@pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "DELETE"])
def test_safe_methods_retry(client: LetMeSendEmail, httpx_mock: Any, method: str) -> None:
    client._config.retries = 1
    url = "https://letmesend.email/api/v1/test"
    _make_sequential_mock(
        httpx_mock,
        url,
        method,
        [
            {"status": 500, "json": {"name": "error", "message": "E"}},
            {"json": {}},
        ],
    )

    with (
        patch("letmesendemail._client.time.sleep") as mock_sleep,
        patch("letmesendemail._client.random.random", return_value=0.5),
    ):
        result = client._request(method, "/test")

    assert result == {}
    mock_sleep.assert_called_once_with(0.075)


# ── Focused error tests ──


def test_401_authentication_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=401,
        json={"message": "Unauthorized", "name": "bad_key"},
    )

    with pytest.raises(AuthenticationError):
        client._request("GET", "/test")


def test_403_authorization_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=403,
        json={"message": "Forbidden", "name": "no_permission"},
    )

    with pytest.raises(AuthorizationError):
        client._request("GET", "/test")


def test_404_not_found_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=404,
        json={"message": "Not Found", "name": "not_found"},
    )

    with pytest.raises(NotFoundError):
        client._request("GET", "/test")


def test_409_conflict_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=409,
        json={"message": "Conflict", "name": "conflict"},
    )

    with pytest.raises(ConflictError):
        client._request("GET", "/test")


def test_500_generic_api_error(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=500,
        json={"message": "Server Error", "name": "server_error"},
    )

    with pytest.raises(ApiError):
        client._request("GET", "/test")


def test_rate_limit_metadata(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=429,
        json={"message": "Rate limited", "name": "rate_limited"},
        headers={
            "Retry-After": "30",
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1700000000",
        },
    )

    with pytest.raises(RateLimitError) as exc:
        client._request("GET", "/test")

    err = exc.value
    assert err.retry_after == 30
    assert err.limit == 100
    assert err.remaining == 0
    assert err.reset_at == "1700000000"


def test_http_date_retry_after(client: LetMeSendEmail, httpx_mock: Any) -> None:
    from datetime import datetime, timedelta, timezone

    future = datetime.now(timezone.utc) + timedelta(seconds=10)
    future_str = future.strftime("%a, %d %b %Y %H:%M:%S %Z")
    httpx_mock.add_response(
        method="GET",
        url="https://letmesend.email/api/v1/test",
        status_code=429,
        json={"message": "Rate limited", "name": "rate_limited"},
        headers={"Retry-After": future_str},
    )

    with pytest.raises(RateLimitError) as exc:
        client._request("GET", "/test")

    assert exc.value.retry_after is not None
    assert exc.value.retry_after > 0


def test_exact_empty_raw_body(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET", url="https://letmesend.email/api/v1/emails", status_code=200, text="null"
    )

    with pytest.raises(ApiError) as exc:
        client._request("GET", "/emails")

    assert exc.value.raw_body == "null"
