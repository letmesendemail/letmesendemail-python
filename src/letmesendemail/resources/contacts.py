"""Contacts resource for the letmesend.email SDK."""

from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlencode

from letmesendemail._models import (
    ContactItem,
    ContactListResponse,
    ContactUpdateResponse,
    PaginationInfo,
    StatusResponse,
)


class ContactsResource:
    """Access the Contacts API."""

    def __init__(self, request_fn: Callable[..., dict[str, Any]]) -> None:
        self._request = request_fn

    def create(
        self,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        is_globally_unsubscribed: bool | None = None,
        categories: list[str] | None = None,
        email_topics: list[str] | None = None,
    ) -> ContactItem:
        """Create a contact."""
        body: dict[str, Any] = {"email": email}
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if phone is not None:
            body["phone"] = phone
        if is_globally_unsubscribed is not None:
            body["is_globally_unsubscribed"] = is_globally_unsubscribed
        if categories is not None:
            body["categories"] = categories
        if email_topics is not None:
            body["email_topics"] = email_topics
        data = self._request("POST", "/contacts", body)
        return _contact_from_dict(data)

    def list(
        self,
        per_page: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> ContactListResponse:
        """List contacts with optional pagination."""
        params: dict[str, str] = {}
        if per_page is not None:
            params["per_page"] = str(per_page)
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        path = f"/contacts?{urlencode(params)}" if params else "/contacts"
        data = self._request("GET", path)
        pagination = data.get("pagination", {})
        return ContactListResponse(
            data=[_contact_from_dict(i) for i in data.get("data", [])],
            pagination=PaginationInfo(
                has_more=pagination.get("has_more", False),
                per_page=pagination.get("per_page", 0),
                fetched=pagination.get("fetched", 0),
                total=pagination.get("total", 0),
            ),
        )

    def get(self, id: str) -> ContactItem:
        """Get a contact by ID."""
        data = self._request("GET", f"/contacts/{id}")
        return _contact_from_dict(data)

    def update(
        self,
        id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        is_globally_unsubscribed: bool | None = None,
        categories: list[str] | None = None,
        email_topics: list[str] | None = None,
        sync_categories: bool | None = None,
        sync_email_topics: bool | None = None,
    ) -> ContactUpdateResponse:
        """Update a contact. Returns only { id } per fixture."""
        body: dict[str, Any] = {}
        if first_name is not None:
            body["first_name"] = first_name
        if last_name is not None:
            body["last_name"] = last_name
        if phone is not None:
            body["phone"] = phone
        if is_globally_unsubscribed is not None:
            body["is_globally_unsubscribed"] = is_globally_unsubscribed
        if categories is not None:
            body["categories"] = categories
        if email_topics is not None:
            body["email_topics"] = email_topics
        if sync_categories is not None:
            body["sync_categories"] = sync_categories
        if sync_email_topics is not None:
            body["sync_email_topics"] = sync_email_topics
        data = self._request("PUT", f"/contacts/{id}", body)
        return ContactUpdateResponse(id=data.get("id", ""))

    def delete(self, id: str) -> StatusResponse:
        """Delete a contact."""
        data = self._request("DELETE", f"/contacts/{id}")
        return StatusResponse(status=data.get("status", ""))


def _contact_from_dict(d: dict[str, Any]) -> ContactItem:
    return ContactItem(
        id=d.get("id", ""),
        email=d.get("email", ""),
        first_name=d.get("first_name"),
        last_name=d.get("last_name"),
        phone=d.get("phone"),
        is_globally_unsubscribed=d.get("is_globally_unsubscribed", False),
        created_at=d.get("created_at", ""),
        categories=d.get("categories", []),
        email_topics=d.get("email_topics", []),
    )
