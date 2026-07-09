from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from letmesendemail._errors import WebhookSigningError, WebhookVerificationError

REQUIRED_HEADERS = [
    "webhook-id",
    "webhook-log-id",
    "webhook-timestamp",
    "webhook-signature",
]

TOLERANCE_SECONDS = 300


def _resolve_header(
    headers: dict[str, str | list[str]],
    name: str,
) -> str | None:
    lower = name.lower()
    candidates = [
        lower,
        f"http_{name.replace('-', '_').lower()}",
    ]
    for key in candidates:
        raw = headers.get(key)
        if raw is not None and raw != "":
            if isinstance(raw, list) and len(raw) > 0:
                return raw[0]
            if isinstance(raw, str):
                return raw
    return None


def verify_webhook(
    payload: str,
    headers: dict[str, str | list[str]],
    secret: str,
    tolerance: int = TOLERANCE_SECONDS,
) -> dict[str, Any]:
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
    now = int(time.time())

    if timestamp <= 0:
        raise WebhookVerificationError("Webhook timestamp must be a positive integer.")

    if timestamp < now - tolerance:
        raise WebhookVerificationError("Webhook timestamp is too old.")

    if timestamp > now + tolerance:
        raise WebhookVerificationError("Webhook timestamp is too far in the future.")

    wid = resolved["webhook-id"]
    wlid = resolved["webhook-log-id"]
    signed_payload = f"{wid}.{wlid}.{timestamp_str}.{payload}"

    raw_secret = secret[6:] if secret.startswith("whsec_") else secret
    try:
        decoded_secret = base64.b64decode(raw_secret)
    except Exception:
        raise WebhookSigningError("Webhook secret could not be decoded.")

    if len(decoded_secret) == 0:
        raise WebhookSigningError("Webhook secret could not be decoded.")

    hex_hash = hmac.new(decoded_secret, signed_payload.encode(), hashlib.sha256).hexdigest()
    expected_signature = base64.b64encode(bytes.fromhex(hex_hash)).decode()

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
