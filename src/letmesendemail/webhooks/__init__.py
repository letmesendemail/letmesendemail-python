"""Webhook signature verification."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Mapping

from letmesendemail._errors import WebhookSigningError, WebhookVerificationError

REQUIRED_HEADERS = [
    "webhook-id",
    "webhook-log-id",
    "webhook-timestamp",
    "webhook-signature",
]

TOLERANCE_SECONDS = 300


def _resolve_header(
    headers: Mapping[str, str | list[str]],
    name: str,
) -> str | None:
    """Resolve a header value with case-insensitive and HTTP_ prefix fallback."""
    lower = name.lower()
    underscore = lower.replace("-", "_")
    candidates: list[str] = []
    for key in headers:
        key_lower = key.lower().replace("-", "_")
        if key_lower == underscore or key_lower == f"http_{underscore}":
            candidates.append(key)
    for key in candidates:
        raw = headers[key]
        if isinstance(raw, list) and raw:
            val = raw[0]
            if val:
                return val
        elif isinstance(raw, str) and raw:
            return raw
    return None


def verify_webhook(
    payload: str,
    headers: dict[str, str | list[str]] | Mapping[str, str | list[str]],
    secret: str,
    tolerance: int = TOLERANCE_SECONDS,
) -> dict[str, Any]:
    """Verify the signature of a webhook payload."""
    resolved: dict[str, str] = {}
    for header_name in REQUIRED_HEADERS:
        value = _resolve_header(headers, header_name)
        if value is None or value == "":
            raise WebhookVerificationError(f"Missing required webhook header: {header_name}.")
        resolved[header_name] = value

    timestamp_str = resolved["webhook-timestamp"]
    if not timestamp_str.isdigit():
        raise WebhookVerificationError("Webhook timestamp is not numeric.")

    timestamp = int(timestamp_str)
    now_int = int(time.time())

    if timestamp <= 0:
        raise WebhookVerificationError("Webhook timestamp must be a positive integer.")

    if timestamp < now_int - tolerance:
        raise WebhookVerificationError("Webhook timestamp is too old.")

    if timestamp > now_int + tolerance:
        raise WebhookVerificationError("Webhook timestamp is too far in the future.")

    signed_payload = (
        f"{resolved['webhook-id']}.{resolved['webhook-log-id']}.{timestamp_str}.{payload}"
    )

    raw_secret = secret[6:] if secret.startswith("whsec_") else secret

    try:
        decoded_secret = base64.b64decode(raw_secret, validate=True)
    except Exception:
        raise WebhookSigningError("Webhook secret could not be decoded.")

    if len(decoded_secret) == 0:
        raise WebhookSigningError("Webhook secret could not be decoded.")

    expected = hmac.new(decoded_secret, signed_payload.encode(), hashlib.sha256).digest()
    expected_signature = base64.b64encode(expected).decode()

    entries = resolved["webhook-signature"].split(" ")
    match_found = False
    for entry in entries:
        entry = entry.strip()
        comma_index = entry.find(",")
        if comma_index == -1:
            continue
        version = entry[:comma_index]
        candidate = entry[comma_index + 1 :]
        if version != "v1":
            continue
        if hmac.compare_digest(candidate, expected_signature):
            match_found = True
            break

    if not match_found:
        raise WebhookVerificationError("No matching webhook signature found.")

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        raise WebhookVerificationError("Webhook payload is not valid JSON.")

    if not isinstance(parsed, dict):
        raise WebhookVerificationError("Webhook payload must be a JSON object.")

    return parsed
