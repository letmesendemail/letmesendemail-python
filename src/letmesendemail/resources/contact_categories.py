from __future__ import annotations

from typing import Any, Callable

from letmesendemail._models import (
    ContactCategoryItem,
    ContactCategoryListResponse,
    PaginationInfo,
    StatusResponse,
)


class ContactCategoriesResource:
    def __init__(self, request_fn: Callable[..., dict[str, Any]]) -> None:
        self._request = request_fn

    def create(self, name: str, slug: str | None = None) -> ContactCategoryItem:
        body: dict[str, Any] = {"name": name}
        if slug is not None:
            body["slug"] = slug
        data = self._request("POST", "/contact-categories", body)
        return ContactCategoryItem(
            id=data.get("id", ""),
            name=data.get("name", ""),
            slug=data.get("slug", ""),
        )

    def list(
        self,
        per_page: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> ContactCategoryListResponse:
        params: dict[str, str] = {}
        if per_page is not None:
            params["per_page"] = str(per_page)
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        query = "&".join(f"{k}={v}" for k, v in params.items())
        path = f"/contact-categories?{query}" if query else "/contact-categories"

        data = self._request("GET", path)
        pagination = data.get("pagination", {})
        return ContactCategoryListResponse(
            data=[
                ContactCategoryItem(
                    id=i.get("id", ""),
                    name=i.get("name", ""),
                    slug=i.get("slug", ""),
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

    def get(self, id: str) -> ContactCategoryItem:
        data = self._request("GET", f"/contact-categories/{id}")
        return ContactCategoryItem(
            id=data.get("id", ""),
            name=data.get("name", ""),
            slug=data.get("slug", ""),
        )

    def update(self, id: str, name: str, slug: str | None = None) -> ContactCategoryItem:
        body: dict[str, Any] = {"name": name}
        if slug is not None:
            body["slug"] = slug
        data = self._request("PUT", f"/contact-categories/{id}", body)
        return ContactCategoryItem(
            id=data.get("id", ""),
            name=data.get("name", ""),
            slug=data.get("slug", ""),
        )

    def delete(self, id: str) -> StatusResponse:
        data = self._request("DELETE", f"/contact-categories/{id}")
        return StatusResponse(
            status=data.get("status", ""),
            message=data.get("message"),
        )
