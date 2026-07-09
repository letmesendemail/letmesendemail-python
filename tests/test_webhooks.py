import base64
import hashlib
import hmac
import json
import time

from letmesendemail._errors import WebhookSigningError, WebhookVerificationError
from letmesendemail.webhooks import verify_webhook


def _make_webhook_data(payload: dict, secret: str, timestamp: int | None = None) -> dict:
    ts = timestamp or int(time.time())
    raw = json.dumps(payload)
    raw_secret = secret[6:] if secret.startswith("whsec_") else secret
    decoded = base64.b64decode(raw_secret)

    to_sign = f"web_123.web_log_123.{ts}.{raw}"
    hex_hash = hmac.new(decoded, to_sign.encode(), hashlib.sha256).hexdigest()
    signature = base64.b64encode(bytes.fromhex(hex_hash)).decode()

    return {
        "payload": raw,
        "headers": {
            "webhook-id": "web_123",
            "webhook-log-id": "web_log_123",
            "webhook-timestamp": str(ts),
            "webhook-signature": f"v1,{signature}",
        },
    }


class TestWebhooks:
    def test_verifies_valid_signature(self):
        raw_secret = base64.b64encode(b"0123456789abcdef0123456789abcdef").decode()
        data = _make_webhook_data({"event": "email.sent"}, raw_secret)
        result = verify_webhook(data["payload"], data["headers"], raw_secret)
        assert result == {"event": "email.sent"}

    def test_verifies_with_whsec_prefix(self):
        raw = base64.b64encode(b"0123456789abcdef0123456789abcdef").decode()
        prefixed = f"whsec_{raw}"
        data = _make_webhook_data({"event": "email.sent"}, prefixed)
        result = verify_webhook(data["payload"], data["headers"], prefixed)
        assert result == {"event": "email.sent"}

    def test_fails_with_wrong_secret(self):
        s1 = base64.b64encode(b"a" * 32).decode()
        s2 = base64.b64encode(b"b" * 32).decode()
        data = _make_webhook_data({"event": "test"}, s1)
        import pytest

        with pytest.raises(WebhookVerificationError):
            verify_webhook(data["payload"], data["headers"], s2)

    def test_fails_expired_timestamp(self):
        secret = base64.b64encode(b"a" * 32).decode()
        old_ts = int(time.time()) - 600
        data = _make_webhook_data({"event": "test"}, secret, old_ts)
        import pytest

        with pytest.raises(WebhookVerificationError, match="too old"):
            verify_webhook(data["payload"], data["headers"], secret)

    def test_fails_future_timestamp(self):
        secret = base64.b64encode(b"a" * 32).decode()
        future_ts = int(time.time()) + 600
        data = _make_webhook_data({"event": "test"}, secret, future_ts)
        import pytest

        with pytest.raises(WebhookVerificationError, match="too far"):
            verify_webhook(data["payload"], data["headers"], secret)

    def test_fails_missing_headers(self):
        import pytest

        with pytest.raises(WebhookVerificationError):
            verify_webhook("{}", {}, "secret")

    def test_fails_non_numeric_timestamp(self):
        secret = base64.b64encode(b"a" * 32).decode()
        data = _make_webhook_data({"event": "test"}, secret)
        data["headers"]["webhook-timestamp"] = "not-a-number"
        import pytest

        with pytest.raises(WebhookVerificationError, match="not numeric"):
            verify_webhook(data["payload"], data["headers"], secret)

    def test_supports_multi_signature(self):
        secret = base64.b64encode(b"a" * 32).decode()
        data = _make_webhook_data({"event": "test"}, secret)
        data["headers"]["webhook-signature"] = f"v1,badsig {data['headers']['webhook-signature']}"
        result = verify_webhook(data["payload"], data["headers"], secret)
        assert result == {"event": "test"}

    def test_ignores_unknown_versions(self):
        secret = base64.b64encode(b"a" * 32).decode()
        data = _make_webhook_data({"event": "test"}, secret)
        data["headers"]["webhook-signature"] = f"v2,ignored {data['headers']['webhook-signature']}"
        result = verify_webhook(data["payload"], data["headers"], secret)
        assert result == {"event": "test"}

    def test_supports_lowercase_headers(self):
        secret = base64.b64encode(b"a" * 32).decode()
        data = _make_webhook_data({"event": "test"}, secret)
        lower = {k.lower(): v for k, v in data["headers"].items()}
        result = verify_webhook(data["payload"], lower, secret)
        assert result == {"event": "test"}

    def test_fails_malformed_json(self):
        secret = base64.b64encode(b"a" * 32).decode()
        ts = int(time.time())
        bad_payload = "not-json"
        to_sign = f"web_123.web_log_123.{ts}.{bad_payload}"
        hex_hash = hmac.new(base64.b64decode(secret), to_sign.encode(), hashlib.sha256).hexdigest()
        sig = base64.b64encode(bytes.fromhex(hex_hash)).decode()
        import pytest

        with pytest.raises(WebhookVerificationError):
            verify_webhook(
                bad_payload,
                {
                    "webhook-id": "web_123",
                    "webhook-log-id": "web_log_123",
                    "webhook-timestamp": str(ts),
                    "webhook-signature": f"v1,{sig}",
                },
                secret,
            )

    def test_fails_bad_secret(self):
        import pytest

        ts = int(time.time())
        with pytest.raises(WebhookSigningError):
            verify_webhook(
                "{}",
                {
                    "webhook-id": "id",
                    "webhook-log-id": "log",
                    "webhook-timestamp": str(ts),
                    "webhook-signature": "v1,sig",
                },
                "not-base64!!!?",
            )
