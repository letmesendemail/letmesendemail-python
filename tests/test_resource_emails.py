"""Tests for the Emails resource — exact request and response assertions."""

from __future__ import annotations

import json
from typing import Any

import pytest

from letmesendemail import LetMeSendEmail
from letmesendemail._models import (
    EmailListResponse,
    SendEmailResponse,
    ShowEmailResponse,
    VerifyEmailResponse,
)

_BASE = "https://letmesend.email/api/v1"
_SEND_RESPONSE = {
    "id": "e1",
    "status": "accepted",
    "emails": ["a@b.com"],
    "restricted_emails": [],
    "duplicate": False,
}


@pytest.fixture
def client() -> LetMeSendEmail:
    return LetMeSendEmail(api_key="test_key", base_url=_BASE)


@pytest.fixture
def email_url() -> str:
    return f"{_BASE}/emails"


# ── Send ──


def test_send_exact_request(client: LetMeSendEmail, httpx_mock: Any, email_url: str) -> None:
    httpx_mock.add_response(method="POST", url=email_url, json=_SEND_RESPONSE)

    client.emails.send(
        from_="a@b.com",
        to=["c@d.com"],
        subject="Hi",
        html="<p>Hi</p>",
        text="Hello",
        type_="transactional",
        event_name="welcome",
        email_topic_id="topic_1",
        reply_to=["reply@b.com"],
        cc=["cc@b.com"],
        bcc=["bcc@b.com"],
        headers={"X-Custom": "val"},
        attachments=[{"name": "f.pdf", "path": "https://ex.com/f.pdf"}],
    )

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/emails")
    body = json.loads(req.content)
    assert body["from"] == "a@b.com"
    assert body["to"] == ["c@d.com"]
    assert body["subject"] == "Hi"
    assert body["html"] == "<p>Hi</p>"
    assert body["text"] == "Hello"
    assert body["type"] == "transactional"
    assert body["event_name"] == "welcome"
    assert body["email_topic_id"] == "topic_1"
    assert body["reply_to"] == ["reply@b.com"]
    assert body["cc"] == ["cc@b.com"]
    assert body["bcc"] == ["bcc@b.com"]
    assert body["headers"] == {"X-Custom": "val"}
    assert body["attachments"] == [{"name": "f.pdf", "path": "https://ex.com/f.pdf"}]


def test_send_with_template_exact_request(
    client: LetMeSendEmail,
    httpx_mock: Any,
    email_url: str,
) -> None:
    httpx_mock.add_response(method="POST", url=email_url, json=_SEND_RESPONSE)

    client.emails.send_with_template(
        from_="a@b.com",
        to=["c@d.com"],
        template_id="tpl_1",
        template_variables=[{"key": "name", "value": "Alice"}],
    )

    req = httpx_mock.get_request()
    assert req.method == "POST"
    body = json.loads(req.content)
    assert body["from"] == "a@b.com"
    assert body["to"] == ["c@d.com"]
    assert body["template_id"] == "tpl_1"
    assert body["template_variables"] == [{"key": "name", "value": "Alice"}]


def test_send_omits_optional_fields(
    client: LetMeSendEmail,
    httpx_mock: Any,
    email_url: str,
) -> None:
    httpx_mock.add_response(method="POST", url=email_url, json=_SEND_RESPONSE)

    client.emails.send(from_="a@b.com", to=["c@d.com"], subject="Hi")

    body = json.loads(httpx_mock.get_request().content)
    assert body == {"from": "a@b.com", "to": ["c@d.com"], "subject": "Hi"}


def test_send_attachment_by_path(
    client: LetMeSendEmail,
    httpx_mock: Any,
    email_url: str,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url=email_url,
        json={
            "id": "e1",
            "status": "accepted",
            "emails": [],
            "restricted_emails": [],
            "duplicate": False,
        },
    )

    client.emails.send(
        from_="a@b.com",
        to=["c@d.com"],
        subject="Hi",
        attachments=[{"name": "f.pdf", "path": "https://ex.com/f.pdf"}],
    )

    body = json.loads(httpx_mock.get_request().content)
    assert body["attachments"] == [{"name": "f.pdf", "path": "https://ex.com/f.pdf"}]


def test_send_attachment_by_content(
    client: LetMeSendEmail,
    httpx_mock: Any,
    email_url: str,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url=email_url,
        json={
            "id": "e1",
            "status": "accepted",
            "emails": [],
            "restricted_emails": [],
            "duplicate": False,
        },
    )

    client.emails.send(
        from_="a@b.com",
        to=["c@d.com"],
        subject="Hi",
        attachments=[{"name": "d.txt", "content": "SGVsbG8="}],
    )

    body = json.loads(httpx_mock.get_request().content)
    assert body["attachments"] == [{"name": "d.txt", "content": "SGVsbG8="}]


def test_send_response_fields(
    client: LetMeSendEmail,
    httpx_mock: Any,
    email_url: str,
) -> None:
    httpx_mock.add_response(
        method="POST",
        url=email_url,
        json={
            "id": "e1",
            "status": "accepted",
            "emails": ["a@b.com"],
            "restricted_emails": ["c@d.com"],
            "duplicate": True,
        },
    )

    result = client.emails.send(from_="a@b.com", to=["c@d.com"], subject="Hi")
    assert isinstance(result, SendEmailResponse)
    assert result.id == "e1"
    assert result.status == "accepted"
    assert result.emails == ["a@b.com"]
    assert result.restricted_emails == ["c@d.com"]
    assert result.duplicate is True


# ── Verify ──


def test_verify_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/emails/verify",
        json={
            "email": "test@test.com",
            "score": 95,
            "status": "deliverable",
            "domain_exists": True,
            "disposable": False,
            "role_based": False,
            "has_mailbox": True,
            "receive_email": True,
            "mx_records": True,
            "valid_syntax": True,
            "belongs_to": None,
        },
    )

    client.emails.verify("test@test.com")

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/emails/verify")
    assert json.loads(req.content) == {"email": "test@test.com"}


def test_verify_response_fields(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/emails/verify",
        json={
            "email": "test@test.com",
            "score": 95,
            "status": "deliverable",
            "domain_exists": True,
            "disposable": False,
            "role_based": False,
            "has_mailbox": True,
            "receive_email": True,
            "mx_records": True,
            "valid_syntax": True,
            "belongs_to": "Acme",
        },
    )

    result = client.emails.verify("test@test.com")
    assert isinstance(result, VerifyEmailResponse)
    assert result.email == "test@test.com"
    assert result.score == 95
    assert result.status == "deliverable"
    assert result.domain_exists is True
    assert result.disposable is False
    assert result.role_based is False
    assert result.has_mailbox is True
    assert result.receive_email is True
    assert result.mx_records is True
    assert result.valid_syntax is True
    assert result.belongs_to == "Acme"


# ── List ──


def test_list_pagination_query(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/emails?per_page=10&after=cursor_a&before=cursor_b",
        json={
            "data": [],
            "pagination": {
                "has_more": False,
                "per_page": 10,
                "fetched": 0,
                "total": 0,
            },
        },
    )

    client.emails.list(per_page=10, after="cursor_a", before="cursor_b")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert "per_page=10" in str(req.url)
    assert "after=cursor_a" in str(req.url)
    assert "before=cursor_b" in str(req.url)


def test_list_response_pagination(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/emails",
        json={
            "data": [
                {
                    "id": "e1",
                    "status": "sent",
                    "subject": "Hi",
                    "type": "transactional",
                    "created_at": "2026-01-01T00:00:00Z",
                    "recipients_count": 1,
                    "attachments_count": 0,
                },
            ],
            "pagination": {
                "has_more": True,
                "per_page": 20,
                "fetched": 1,
                "total": 50,
            },
        },
    )

    result = client.emails.list()
    assert isinstance(result, EmailListResponse)
    assert len(result.data) == 1
    assert result.data[0].id == "e1"
    assert result.data[0].status == "sent"
    assert result.pagination.has_more is True
    assert result.pagination.per_page == 20
    assert result.pagination.fetched == 1
    assert result.pagination.total == 50


# ── Get ──


def test_get_exact_path(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/emails/e1",
        json={
            "id": "e1",
            "status": "sent",
            "type": "transactional",
            "created_at": "2026-01-01T00:00:00Z",
            "recipients_count": 2,
            "attachments_count": 1,
            "recipients": [],
            "attachments": [],
        },
    )

    client.emails.get("e1")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/emails/e1")


def test_get_response_full(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/emails/e1",
        json={
            "id": "e1",
            "status": "sent",
            "subject": "Hello",
            "type": "transactional",
            "created_at": "2026-01-01T00:00:00Z",
            "recipients_count": 2,
            "attachments_count": 1,
            "recipients": [
                {
                    "type": "to",
                    "status": "delivered",
                    "email_address": "a@b.com",
                    "is_suppressed": False,
                    "open_count": 1,
                    "click_count": 0,
                },
                {
                    "type": "cc",
                    "status": "delivered",
                    "email_address": "c@d.com",
                    "is_suppressed": False,
                    "open_count": 0,
                    "click_count": 0,
                },
            ],
            "attachments": [
                {
                    "id": "att_1",
                    "name": "f.pdf",
                    "mime": "application/pdf",
                    "size": 1024,
                    "download_url": "https://ex.com/f.pdf",
                },
            ],
        },
    )

    result = client.emails.get("e1")
    assert isinstance(result, ShowEmailResponse)
    assert result.id == "e1"
    assert result.status == "sent"
    assert result.recipients_count == 2
    assert result.attachments_count == 1
    assert len(result.recipients) == 2
    assert result.recipients[0].email_address == "a@b.com"
    assert result.recipients[0].type == "to"
    assert len(result.attachments) == 1
    assert result.attachments[0].name == "f.pdf"
    assert result.attachments[0].download_url == "https://ex.com/f.pdf"
