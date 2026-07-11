"""Tests for the Domains resource — exact request and response assertions."""

from __future__ import annotations

import json
from typing import Any

import pytest

from letmesendemail import LetMeSendEmail
from letmesendemail._models import DomainItem, DomainListResponse, StatusResponse

_BASE = "https://letmesend.email/api/v1"


@pytest.fixture
def client() -> LetMeSendEmail:
    return LetMeSendEmail(api_key="test_key", base_url=_BASE)


def test_list_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/domains",
        json={
            "data": [],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 0, "total": 0},
        },
    )

    client.domains.list()

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/domains")


def test_list_pagination_query(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/domains?per_page=10",
        json={
            "data": [],
            "pagination": {"has_more": False, "per_page": 10, "fetched": 0, "total": 0},
        },
    )

    client.domains.list(per_page=10)

    req = httpx_mock.get_request()
    assert "per_page=10" in str(req.url)


def test_list_response_type(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/domains",
        json={
            "data": [
                {
                    "id": "d1",
                    "domain_name": "example.com",
                    "status": "verified",
                    "created_at": "2026-01-01T00:00:00Z",
                },
            ],
            "pagination": {"has_more": False, "per_page": 20, "fetched": 1, "total": 1},
        },
    )

    result = client.domains.list()
    assert isinstance(result, DomainListResponse)
    assert len(result.data) == 1
    assert result.data[0].id == "d1"
    assert result.data[0].domain_name == "example.com"
    assert result.data[0].status == "verified"
    assert result.pagination.total == 1


def test_get_exact_path(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/domains/d1",
        json={
            "id": "d1",
            "domain_name": "example.com",
            "status": "verified",
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    client.domains.get("d1")

    req = httpx_mock.get_request()
    assert req.method == "GET"
    assert str(req.url).endswith("/domains/d1")


def test_get_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/domains/d1",
        json={
            "id": "d1",
            "domain_name": "example.com",
            "status": "verified",
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    result = client.domains.get("d1")
    assert isinstance(result, DomainItem)
    assert result.domain_name == "example.com"
    assert result.status == "verified"


def test_verify_exact_request(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(method="POST", url=f"{_BASE}/domains/verify", json={"status": "ok"})

    client.domains.verify("example.com")

    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url).endswith("/domains/verify")
    assert json.loads(req.content) == {"domain": "example.com"}


def test_verify_response(client: LetMeSendEmail, httpx_mock: Any) -> None:
    httpx_mock.add_response(method="POST", url=f"{_BASE}/domains/verify", json={"status": "ok"})

    result = client.domains.verify("example.com")
    assert isinstance(result, StatusResponse)
    assert result.status == "ok"
