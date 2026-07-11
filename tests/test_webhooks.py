"""Tests for webhook signature verification."""

from __future__ import annotations

import base64
import hashlib
import hmac
from unittest.mock import patch

import pytest

from letmesendemail import WebhookSigningError, WebhookVerificationError
from letmesendemail.webhooks import verify_webhook

RAW_SECRET = b"whsec_test_secret_key"
SECRET_B64 = base64.b64encode(RAW_SECRET).decode()
PAYLOAD = '{"event":"email.sent"}'
WEBHOOK_ID = "msg_123"
WEBHOOK_LOG_ID = "log_456"
TIMESTAMP = "2000000000"

_SIGNED_PAYLOAD = f"{WEBHOOK_ID}.{WEBHOOK_LOG_ID}.{TIMESTAMP}.{PAYLOAD}"
_EXPECTED_SIG = base64.b64encode(
    hmac.new(RAW_SECRET, _SIGNED_PAYLOAD.encode(), hashlib.sha256).digest()
).decode()

VALID_HEADERS: dict[str, str] = {
    "webhook-id": WEBHOOK_ID,
    "webhook-log-id": WEBHOOK_LOG_ID,
    "webhook-timestamp": TIMESTAMP,
    "webhook-signature": f"v1,{_EXPECTED_SIG}",
}


def test_valid_signature() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, VALID_HEADERS, SECRET_B64)
    assert result == {"event": "email.sent"}


def test_valid_signature_whsec_prefix() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, VALID_HEADERS, f"whsec_{SECRET_B64}")
    assert result == {"event": "email.sent"}


def test_wrong_secret() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        with pytest.raises(WebhookVerificationError):
            verify_webhook(PAYLOAD, VALID_HEADERS, base64.b64encode(b"wrong_secret").decode())


@pytest.mark.parametrize(
    "missing",
    [
        "webhook-id",
        "webhook-log-id",
        "webhook-timestamp",
        "webhook-signature",
    ],
)
def test_missing_header(missing: str) -> None:
    headers = dict(VALID_HEADERS)
    del headers[missing]
    with pytest.raises(WebhookVerificationError):
        verify_webhook(PAYLOAD, headers, SECRET_B64)


def test_expired_timestamp() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000060000):
        with pytest.raises(WebhookVerificationError):
            verify_webhook(PAYLOAD, VALID_HEADERS, SECRET_B64)


def test_future_timestamp() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=1999940000):
        with pytest.raises(WebhookVerificationError):
            verify_webhook(PAYLOAD, VALID_HEADERS, SECRET_B64)


def test_non_numeric_timestamp() -> None:
    headers = dict(VALID_HEADERS)
    headers["webhook-timestamp"] = "abc"
    with pytest.raises(WebhookVerificationError):
        verify_webhook(PAYLOAD, headers, SECRET_B64)


def test_zero_timestamp() -> None:
    headers = dict(VALID_HEADERS)
    headers["webhook-timestamp"] = "0"
    with pytest.raises(WebhookVerificationError):
        verify_webhook(PAYLOAD, headers, SECRET_B64)


def test_multiple_signatures_one_matches() -> None:
    wrong_secret = b"wrong_secret"
    wrong_sig = base64.b64encode(
        hmac.new(wrong_secret, _SIGNED_PAYLOAD.encode(), hashlib.sha256).digest()
    ).decode()
    headers = dict(VALID_HEADERS)
    headers["webhook-signature"] = f"v1,{wrong_sig} v1,{_EXPECTED_SIG}"

    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, headers, SECRET_B64)
    assert result == {"event": "email.sent"}


def test_no_v1_match() -> None:
    headers = dict(VALID_HEADERS)
    headers["webhook-signature"] = f"v2,{_EXPECTED_SIG}"

    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        with pytest.raises(WebhookVerificationError):
            verify_webhook(PAYLOAD, headers, SECRET_B64)


@pytest.mark.parametrize("key", ["Webhook-Id", "WEBHOOK-ID", "Webhook_ID"])
def test_case_insensitive_headers(key: str) -> None:
    headers = {
        key: WEBHOOK_ID,
        "webhook-log-id": WEBHOOK_LOG_ID,
        "webhook-timestamp": TIMESTAMP,
        "webhook-signature": f"v1,{_EXPECTED_SIG}",
    }
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, headers, SECRET_B64)
    assert result == {"event": "email.sent"}


def test_http_prefixed_headers() -> None:
    headers = {
        "HTTP_WEBHOOK_ID": WEBHOOK_ID,
        "HTTP_WEBHOOK_LOG_ID": WEBHOOK_LOG_ID,
        "HTTP_WEBHOOK_TIMESTAMP": TIMESTAMP,
        "HTTP_WEBHOOK_SIGNATURE": f"v1,{_EXPECTED_SIG}",
    }
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, headers, SECRET_B64)
    assert result == {"event": "email.sent"}


def test_map_string_string_headers() -> None:
    headers: dict[str, str] = {
        "webhook-id": WEBHOOK_ID,
        "webhook-log-id": WEBHOOK_LOG_ID,
        "webhook-timestamp": TIMESTAMP,
        "webhook-signature": f"v1,{_EXPECTED_SIG}",
    }
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, headers, SECRET_B64)
    assert result == {"event": "email.sent"}


def test_map_string_list_headers() -> None:
    headers: dict[str, list[str]] = {
        "webhook-id": [WEBHOOK_ID],
        "webhook-log-id": [WEBHOOK_LOG_ID],
        "webhook-timestamp": [TIMESTAMP],
        "webhook-signature": [f"v1,{_EXPECTED_SIG}"],
    }
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, headers, SECRET_B64)
    assert result == {"event": "email.sent"}


def test_invalid_payload_json() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        with pytest.raises(WebhookVerificationError):
            verify_webhook("not-json", VALID_HEADERS, SECRET_B64)


def test_non_dict_payload() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        with pytest.raises(WebhookVerificationError):
            verify_webhook("[]", VALID_HEADERS, SECRET_B64)


def test_bad_secret_not_base64() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        with pytest.raises(WebhookSigningError):
            verify_webhook(PAYLOAD, VALID_HEADERS, "!!!")


def test_whsec_prefixed_secret() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        result = verify_webhook(PAYLOAD, VALID_HEADERS, f"whsec_{SECRET_B64}")
    assert result == {"event": "email.sent"}


def test_custom_tolerance() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        tolerance = 60
        result = verify_webhook(PAYLOAD, VALID_HEADERS, SECRET_B64, tolerance=tolerance)
    assert result == {"event": "email.sent"}


def test_empty_secret_raises_signing_error() -> None:
    with patch("letmesendemail.webhooks.time.time", return_value=2000000000):
        with pytest.raises(WebhookSigningError):
            verify_webhook(PAYLOAD, VALID_HEADERS, base64.b64encode(b"").decode())
