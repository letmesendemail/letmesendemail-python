"""Emails resource for the letmesend.email SDK."""

from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlencode

from letmesendemail._models import (
    EmailAttachment,
    EmailListItem,
    EmailListResponse,
    PaginationInfo,
    Recipient,
    SendAttachment,
    SendEmailResponse,
    ShowEmailResponse,
    VerifyEmailResponse,
)


def _serialize_attachments(attachments: list[SendAttachment]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for a in attachments:
        out: dict[str, Any] = {"name": a["name"]}
        if "path" in a:
            out["path"] = a["path"]
        if "content" in a:
            out["content"] = a["content"]
        if "mime" in a:
            out["mime"] = a["mime"]
        if a.get("content_id"):
            out["content_id"] = a.get("content_id")
        if a.get("content_disposition"):
            out["content_disposition"] = a.get("content_disposition")
        result.append(out)
    return result


class EmailsResource:
    """Access the Emails API."""

    def __init__(self, request_fn: Callable[..., dict[str, Any]]) -> None:
        self._request = request_fn

    def send(
        self,
        from_: str,
        to: list[str],
        subject: str,
        html: str | None = None,
        text: str | None = None,
        type_: str | None = None,
        event_name: str | None = None,
        email_topic_id: str | None = None,
        reply_to: list[str] | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        headers: dict[str, str] | None = None,
        attachments: list[SendAttachment] | None = None,
        idempotency_key: str | None = None,
    ) -> SendEmailResponse:
        """Send an email."""
        body: dict[str, Any] = {"from": from_, "to": to, "subject": subject}
        if html is not None:
            body["html"] = html
        if text is not None:
            body["text"] = text
        if type_ is not None:
            body["type"] = type_
        if event_name is not None:
            body["event_name"] = event_name
        if email_topic_id is not None:
            body["email_topic_id"] = email_topic_id
        if reply_to is not None:
            body["reply_to"] = reply_to
        if cc is not None:
            body["cc"] = cc
        if bcc is not None:
            body["bcc"] = bcc
        if headers is not None:
            body["headers"] = headers
        if attachments is not None:
            body["attachments"] = _serialize_attachments(attachments)

        extra_headers = {}
        if idempotency_key is not None:
            extra_headers["Idempotency-Key"] = idempotency_key

        data = self._request("POST", "/emails", body, extra_headers)
        return SendEmailResponse(
            id=data.get("id", ""),
            status=data.get("status", ""),
            emails=data.get("emails", []),
            restricted_emails=data.get("restricted_emails", []),
            duplicate=data.get("duplicate", False),
        )

    def send_with_template(
        self,
        from_: str,
        to: list[str],
        template_id: str,
        subject: str | None = None,
        template_variables: list[dict[str, Any]] | None = None,
        type_: str | None = None,
        event_name: str | None = None,
        email_topic_id: str | None = None,
        reply_to: list[str] | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        headers: dict[str, str] | None = None,
        attachments: list[SendAttachment] | None = None,
        idempotency_key: str | None = None,
    ) -> SendEmailResponse:
        """Send an email with a template."""
        body: dict[str, Any] = {"from": from_, "to": to, "template_id": template_id}
        if subject is not None:
            body["subject"] = subject
        if template_variables is not None:
            body["template_variables"] = template_variables
        if type_ is not None:
            body["type"] = type_
        if event_name is not None:
            body["event_name"] = event_name
        if email_topic_id is not None:
            body["email_topic_id"] = email_topic_id
        if reply_to is not None:
            body["reply_to"] = reply_to
        if cc is not None:
            body["cc"] = cc
        if bcc is not None:
            body["bcc"] = bcc
        if headers is not None:
            body["headers"] = headers
        if attachments is not None:
            body["attachments"] = _serialize_attachments(attachments)

        extra_headers = {}
        if idempotency_key is not None:
            extra_headers["Idempotency-Key"] = idempotency_key

        data = self._request("POST", "/emails", body, extra_headers)
        return SendEmailResponse(
            id=data.get("id", ""),
            status=data.get("status", ""),
            emails=data.get("emails", []),
            restricted_emails=data.get("restricted_emails", []),
            duplicate=data.get("duplicate", False),
        )

    def verify(self, email: str) -> VerifyEmailResponse:
        """Verify an email address."""
        data = self._request("POST", "/emails/verify", {"email": email})
        return VerifyEmailResponse(
            email=data.get("email", ""),
            score=data.get("score", 0),
            status=data.get("status", ""),
            domain_exists=data.get("domain_exists", False),
            disposable=data.get("disposable", False),
            role_based=data.get("role_based", False),
            has_mailbox=data.get("has_mailbox", False),
            receive_email=data.get("receive_email", False),
            mx_records=data.get("mx_records", False),
            valid_syntax=data.get("valid_syntax", False),
            belongs_to=data.get("belongs_to"),
        )

    def list(
        self,
        per_page: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> EmailListResponse:
        """List emails with optional pagination."""
        params: dict[str, str] = {}
        if per_page is not None:
            params["per_page"] = str(per_page)
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        path = f"/emails?{urlencode(params)}" if params else "/emails"

        data = self._request("GET", path)
        pagination = data.get("pagination", {})
        return EmailListResponse(
            data=[
                EmailListItem(
                    id=i.get("id", ""),
                    status=i.get("status", ""),
                    subject=i.get("subject"),
                    event_name=i.get("event_name"),
                    type=i.get("type", ""),
                    created_at=i.get("created_at", ""),
                    sent_at=i.get("sent_at"),
                    recipients_count=i.get("recipients_count", 0),
                    attachments_count=i.get("attachments_count", 0),
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

    def get(self, id: str) -> ShowEmailResponse:
        """Get a single email by ID."""
        data = self._request("GET", f"/emails/{id}")
        return ShowEmailResponse(
            id=data.get("id", ""),
            status=data.get("status", ""),
            subject=data.get("subject"),
            event_name=data.get("event_name"),
            type=data.get("type", ""),
            created_at=data.get("created_at", ""),
            sent_at=data.get("sent_at"),
            recipients_count=data.get("recipients_count", 0),
            attachments_count=data.get("attachments_count", 0),
            recipients=[
                Recipient(
                    type=r.get("type", ""),
                    status=r.get("status", ""),
                    email_address=r.get("email_address", ""),
                    bounce_type=r.get("bounce_type"),
                    bounce_reason=r.get("bounce_reason"),
                    bounced_at=r.get("bounced_at"),
                    complaint_type=r.get("complaint_type"),
                    complained_at=r.get("complained_at"),
                    is_suppressed=r.get("is_suppressed", False),
                    suppression_reason=r.get("suppression_reason"),
                    opened_at=r.get("opened_at"),
                    open_count=r.get("open_count", 0),
                    clicked_at=r.get("clicked_at"),
                    click_count=r.get("click_count", 0),
                    failed_at=r.get("failed_at"),
                    error_message=r.get("error_message"),
                    delivered_at=r.get("delivered_at"),
                    sent_at=r.get("sent_at"),
                )
                for r in data.get("recipients", [])
            ],
            attachments=[
                EmailAttachment(
                    id=a.get("id", ""),
                    name=a.get("name", ""),
                    mime=a.get("mime", ""),
                    content_id=a.get("content_id", ""),
                    content_disposition=a.get("content_disposition", ""),
                    size=a.get("size", 0),
                    download_url=a.get("download_url", ""),
                )
                for a in data.get("attachments", [])
            ],
        )
