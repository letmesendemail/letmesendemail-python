from __future__ import annotations

from typing import Any, Callable

from letmesendemail._models import (
    EmailTopicItem,
    EmailTopicListResponse,
    PaginationInfo,
    StatusResponse,
)


class EmailTopicsResource:
    def __init__(self, request_fn: Callable[..., dict[str, Any]]) -> None:
        self._request = request_fn

    def create(
        self,
        name: str,
        slug: str,
        auto_subscribe: bool | None = None,
        public: bool | None = None,
        description: str | None = None,
        domain_id: str | None = None,
    ) -> EmailTopicItem:
        body: dict[str, Any] = {"name": name, "slug": slug}
        if auto_subscribe is not None:
            body["auto_subscribe"] = auto_subscribe
        if public is not None:
            body["public"] = public
        if description is not None:
            body["description"] = description
        if domain_id is not None:
            body["domain"] = {"id": domain_id}

        data = self._request("POST", "/email-topics", body)
        return _topic_from_dict(data)

    def list(
        self,
        per_page: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> EmailTopicListResponse:
        params: dict[str, str] = {}
        if per_page is not None:
            params["per_page"] = str(per_page)
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        query = "&".join(f"{k}={v}" for k, v in params.items())
        path = f"/email-topics?{query}" if query else "/email-topics"

        data = self._request("GET", path)
        pagination = data.get("pagination", {})
        return EmailTopicListResponse(
            data=[_topic_from_dict(i) for i in data.get("data", [])],
            pagination=PaginationInfo(
                has_more=pagination.get("has_more", False),
                per_page=pagination.get("per_page", 0),
                fetched=pagination.get("fetched", 0),
                total=pagination.get("total", 0),
            ),
        )

    def get(self, id: str) -> EmailTopicItem:
        data = self._request("GET", f"/email-topics/{id}")
        return _topic_from_dict(data)

    def update(
        self,
        id: str,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        public: bool | None = None,
        auto_subscribe: bool | None = None,
    ) -> EmailTopicItem:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        if description is not None:
            body["description"] = description
        if public is not None:
            body["public"] = public
        if auto_subscribe is not None:
            body["auto_subscribe"] = auto_subscribe

        data = self._request("PUT", f"/email-topics/{id}", body)
        return _topic_from_dict(data)

    def delete(self, id: str) -> StatusResponse:
        data = self._request("DELETE", f"/email-topics/{id}")
        return StatusResponse(
            status=data.get("status", ""),
            message=data.get("message"),
        )


def _topic_from_dict(d: dict[str, Any]) -> EmailTopicItem:
    return EmailTopicItem(
        id=d.get("id", ""),
        name=d.get("name", ""),
        slug=d.get("slug", ""),
        description=d.get("description"),
        auto_subscribe=d.get("auto_subscribe", False),
        public=d.get("public", False),
        created_at=d.get("created_at", ""),
        domain=d.get("domain"),
    )
