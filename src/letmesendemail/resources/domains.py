from __future__ import annotations

from typing import Any, Callable

from letmesendemail._models import DomainItem, DomainListResponse, PaginationInfo, StatusResponse


class DomainsResource:
    def __init__(self, request_fn: Callable[..., dict[str, Any]]) -> None:
        self._request = request_fn

    def list(
        self,
        per_page: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> DomainListResponse:
        params: dict[str, str] = {}
        if per_page is not None:
            params["per_page"] = str(per_page)
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        query = "&".join(f"{k}={v}" for k, v in params.items())
        path = f"/domains?{query}" if query else "/domains"

        data = self._request("GET", path)
        pagination = data.get("pagination", {})
        return DomainListResponse(
            data=[
                DomainItem(
                    id=i.get("id", ""),
                    domain_name=i.get("domain_name", ""),
                    status=i.get("status", ""),
                    created_at=i.get("created_at", ""),
                )
                for i in data.get("data", [])
            ],
            pagination=PaginationInfo(
                has_more=pagination.get("has_more", False),
                per_page=pagination.get("per_page", 0),
                fetched=pagination.get("fetched", 0),
                total=pagination.get("total", 0),
            ),
        )

    def get(self, id: str) -> DomainItem:
        data = self._request("GET", f"/domains/{id}")
        return DomainItem(
            id=data.get("id", ""),
            domain_name=data.get("domain_name", ""),
            status=data.get("status", ""),
            created_at=data.get("created_at", ""),
        )

    def verify(self, domain: str) -> StatusResponse:
        data = self._request("POST", "/domains/verify", {"domain": domain})
        return StatusResponse(status=data.get("status", ""))
