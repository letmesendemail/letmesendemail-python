"""Tests for the Contacts resource — exact request and response assertions."""

from __future__ import annotations

import json
from typing import Any

import pytest

from letmesendemail import LetMeSendEmail
from letmesendemail._models import (
    ContactItem,
    ContactListResponse,
    ContactUpdateResponse,
    StatusResponse,
)

_BASE = "https://letmesend.email/api/v1"


@pytest.fixture
def client() -> LetMeSendEmail:
    return LetMeSendEmail(api_key="test_key", base_url=_BASE)


def test_create_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/contacts",
        json={
            "id": "c1",
            "email": "test@test.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "is_globally_unsubscribed": False,
            "created_at": "2026-01-01T00:00:00Z",
            "categories": [],
            "email_topics": [],
        },
    )

    client.contacts.create(
        email="test@test.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
    )

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/contacts")
    body = json.loads(req.content)
    assert body["email"] == "test@test.com"
    assert body["first_name"] == "John"
    assert body["last_name"] == "Doe"
    assert body["phone"] == "+1234567890"


def test_create_omits_optional_fields(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/contacts",
        json={
            "id": "c1",
            "email": "a@b.com",
            "is_globally_unsubscribed": False,
            "created_at": "2026-01-01T00:00:00Z",
            "categories": [],
            "email_topics": [],
        },
    )

    client.contacts.create(email="a@b.com")

    body = json.loads(httpx_mock.get_request().content)
    assert body == {"email": "a@b.com"}


def test_create_response_fields(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/contacts",
        json={
            "id": "c1",
            "email": "test@test.com",
            "first_name": "John",
            "is_globally_unsubscribed": False,
            "created_at": "2026-01-01T00:00:00Z",
            "categories": [],
            "email_topics": [],
        },
    )

    result = client.contacts.create(email="test@test.com")
    assert isinstance(result, ContactItem)
    assert result.id == "c1"
    assert result.email == "test@test.com"
    assert result.first_name == "John"


def test_list_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/contacts?per_page=5&after=cursor",
        json={
            "data": [],
            "pagination": {
                "has_more": False,
                "per_page": 5,
                "fetched": 0,
                "total": 0,
            },
        },
    )

    client.contacts.list(per_page=5, after="cursor")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert "per_page=5" in str(req.url)
    assert "after=cursor" in str(req.url)


def test_list_response_type(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/contacts",
        json={
            "data": [
                {
                    "id": "c1",
                    "email": "a@b.com",
                    "is_globally_unsubscribed": False,
                    "created_at": "2026-01-01T00:00:00Z",
                    "categories": [],
                    "email_topics": [],
                }
            ],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 1, "total": 1},
        },
    )

    result = client.contacts.list()
    assert isinstance(result, ContactListResponse)
    assert len(result.data) == 1
    assert result.data[0].id == "c1"
    assert result.pagination.total == 1


def test_get_exact_path(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/contacts/c1",
        json={
            "id": "c1",
            "email": "a@b.com",
            "is_globally_unsubscribed": False,
            "created_at": "2026-01-01T00:00:00Z",
            "categories": [],
            "email_topics": [],
        },
    )

    client.contacts.get("c1")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/contacts/c1")


def test_update_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(method="PUT", url=f"{_BASE}/contacts/c1", json={"id": "c1"})

    client.contacts.update(
        id="c1",
        first_name="Jane",
        sync_categories=True,
    )

    req = httpx_mock.get_request()
    assert req.method == "PUT"
    assert str(req.url).endswith("/contacts/c1")
    body = json.loads(req.content)
    assert body["first_name"] == "Jane"
    assert body["sync_categories"] is True


def test_update_response_type(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(method="PUT", url=f"{_BASE}/contacts/c1", json={"id": "c1"})

    result = client.contacts.update(id="c1", first_name="Jane")
    assert isinstance(result, ContactUpdateResponse)
    assert result.id == "c1"


def test_delete_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/contacts/c1",
        json={"status": "deleted"},
    )

    client.contacts.delete("c1")

    req = httpx_mock.get_request()
    assert req.method == "DELETE"
    assert str(req.url).endswith("/contacts/c1")


def test_delete_response_type(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/contacts/c1",
        json={"status": "deleted", "message": "OK"},
    )

    result = client.contacts.delete("c1")
    assert isinstance(result, StatusResponse)
    assert result.status == "deleted"
