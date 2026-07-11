"""Tests for Contact Categories and Email Topics resources."""

from __future__ import annotations

import json
from typing import Any

import pytest

from letmesendemail import LetMeSendEmail
from letmesendemail._models import (
    ContactCategoryItem,
    ContactCategoryListResponse,
    EmailTopicItem,
    EmailTopicListResponse,
    StatusResponse,
)

_BASE = "https://letmesend.email/api/v1"


@pytest.fixture
def client() -> LetMeSendEmail:
    return LetMeSendEmail(api_key="test_key", base_url=_BASE)


# ── Contact Categories ──


def test_cc_create_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/contact-categories",
        json={
            "id": "cc1",
            "name": "Newsletter",
            "slug": "newsletter",
        },
    )

    client.contact_categories.create("Newsletter", slug="newsletter")

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/contact-categories")
    assert json.loads(req.content) == {"name": "Newsletter", "slug": "newsletter"}


def test_cc_create_omits_slug(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/contact-categories",
        json={
            "id": "cc1",
            "name": "Newsletter",
            "slug": "",
        },
    )

    client.contact_categories.create("Newsletter")

    assert json.loads(httpx_mock.get_request().content) == {"name": "Newsletter"}


def test_cc_create_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/contact-categories",
        json={
            "id": "cc1",
            "name": "Newsletter",
            "slug": "newsletter",
        },
    )

    result = client.contact_categories.create("Newsletter")
    assert isinstance(result, ContactCategoryItem)
    assert result.id == "cc1"
    assert result.name == "Newsletter"


def test_cc_list_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/contact-categories",
        json={
            "data": [],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 0, "total": 0},
        },
    )

    client.contact_categories.list()

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/contact-categories")


def test_cc_list_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/contact-categories",
        json={
            "data": [{"id": "cc1", "name": "Newsletter", "slug": "newsletter"}],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 1, "total": 1},
        },
    )

    result = client.contact_categories.list()
    assert isinstance(result, ContactCategoryListResponse)
    assert len(result.data) == 1
    assert result.data[0].slug == "newsletter"


def test_cc_get_exact_path(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/contact-categories/cc1",
        json={
            "id": "cc1",
            "name": "Newsletter",
            "slug": "newsletter",
        },
    )

    client.contact_categories.get("cc1")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/contact-categories/cc1")


def test_cc_update_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="PUT",
        url=f"{_BASE}/contact-categories/cc1",
        json={
            "id": "cc1",
            "name": "Updates",
            "slug": "updates",
        },
    )

    client.contact_categories.update("cc1", "Updates", slug="updates")

    req = httpx_mock.get_request()
    assert req.method == "PUT"
    assert str(req.url).endswith("/contact-categories/cc1")
    assert json.loads(req.content) == {"name": "Updates", "slug": "updates"}


def test_cc_update_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="PUT",
        url=f"{_BASE}/contact-categories/cc1",
        json={
            "id": "cc1",
            "name": "Updates",
            "slug": "updates",
        },
    )

    result = client.contact_categories.update("cc1", "Updates")
    assert isinstance(result, ContactCategoryItem)
    assert result.name == "Updates"


def test_cc_delete_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/contact-categories/cc1",
        json={"status": "deleted", "message": "OK"},
    )

    client.contact_categories.delete("cc1")

    req = httpx_mock.get_request()
    assert req.method == "DELETE"
    assert str(req.url).endswith("/contact-categories/cc1")


def test_cc_delete_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/contact-categories/cc1",
        json={"status": "deleted", "message": "OK"},
    )

    result = client.contact_categories.delete("cc1")
    assert isinstance(result, StatusResponse)
    assert result.status == "deleted"
    assert result.message == "OK"


# ── Email Topics ──


def test_et_create_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/email-topics",
        json={
            "id": "et1",
            "name": "Product Update",
            "slug": "product-update",
            "auto_subscribe": True,
            "public": True,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    client.email_topics.create("Product Update", "product-update", auto_subscribe=True, public=True)

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/email-topics")
    body = json.loads(req.content)
    assert body["name"] == "Product Update"
    assert body["slug"] == "product-update"
    assert body["auto_subscribe"] is True
    assert body["public"] is True


def test_et_create_with_domain(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/email-topics",
        json={
            "id": "et1",
            "name": "Updates",
            "slug": "updates",
            "auto_subscribe": False,
            "public": False,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    client.email_topics.create("Updates", "updates", domain_id="dom_1")

    body = json.loads(httpx_mock.get_request().content)
    assert body["domain"] == {"id": "dom_1"}


def test_et_create_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/email-topics",
        json={
            "id": "et1",
            "name": "Product Update",
            "slug": "product-update",
            "auto_subscribe": True,
            "public": True,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    result = client.email_topics.create("Product Update", "product-update")
    assert isinstance(result, EmailTopicItem)
    assert result.id == "et1"
    assert result.name == "Product Update"
    assert result.auto_subscribe is True


def test_et_list_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/email-topics",
        json={
            "data": [],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 0, "total": 0},
        },
    )

    client.email_topics.list()

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/email-topics")


def test_et_list_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/email-topics",
        json={
            "data": [
                {
                    "id": "et1",
                    "name": "Updates",
                    "slug": "updates",
                    "auto_subscribe": False,
                    "public": False,
                    "created_at": "2026-01-01T00:00:00Z",
                }
            ],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 1, "total": 1},
        },
    )

    result = client.email_topics.list()
    assert isinstance(result, EmailTopicListResponse)
    assert len(result.data) == 1
    assert result.data[0].slug == "updates"


def test_et_get_exact_path(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/email-topics/et1",
        json={
            "id": "et1",
            "name": "Updates",
            "slug": "updates",
            "auto_subscribe": False,
            "public": False,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    client.email_topics.get("et1")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/email-topics/et1")


def test_et_update_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="PUT",
        url=f"{_BASE}/email-topics/et1",
        json={
            "id": "et1",
            "name": "Renamed",
            "slug": "renamed",
            "auto_subscribe": True,
            "public": True,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    client.email_topics.update("et1", name="Renamed", slug="renamed", public=True)

    req = httpx_mock.get_request()
    assert req.method == "PUT"
    assert str(req.url).endswith("/email-topics/et1")
    body = json.loads(req.content)
    assert body["name"] == "Renamed"
    assert body["slug"] == "renamed"
    assert body["public"] is True


def test_et_update_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="PUT",
        url=f"{_BASE}/email-topics/et1",
        json={
            "id": "et1",
            "name": "Renamed",
            "slug": "renamed",
            "auto_subscribe": False,
            "public": False,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    result = client.email_topics.update("et1", name="Renamed")
    assert isinstance(result, EmailTopicItem)
    assert result.name == "Renamed"


def test_et_delete_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/email-topics/et1",
        json={"status": "deleted", "message": "OK"},
    )

    client.email_topics.delete("et1")

    req = httpx_mock.get_request()
    assert req.method == "DELETE"
    assert str(req.url).endswith("/email-topics/et1")


def test_et_delete_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/email-topics/et1",
        json={"status": "deleted", "message": "OK"},
    )

    result = client.email_topics.delete("et1")
    assert isinstance(result, StatusResponse)
    assert result.status == "deleted"
    assert result.message == "OK"
