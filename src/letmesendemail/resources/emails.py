from __future__ import annotations

from typing import Any, Callable

from letmesendemail._models import (
    EmailListItem,
    EmailListResponse,
    PaginationInfo,
    SendEmailResponse,
    ShowEmailResponse,
    VerifyEmailResponse,
)


class EmailsResource:
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
        attachments: list[dict[str, Any]] | None = None,
        idempotency_key: str | None = None,
    ) -> SendEmailResponse:
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
            body["attachments"] = attachments

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
        attachments: list[dict[str, Any]] | None = None,
        idempotency_key: str | None = None,
    ) -> SendEmailResponse:
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
            body["attachments"] = attachments

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
        params: dict[str, str] = {}
        if per_page is not None:
            params["per_page"] = str(per_page)
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        query = "&".join(f"{k}={v}" for k, v in params.items())
        path = f"/emails?{query}" if query else "/emails"

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
            recipients=data.get("recipients", []),
            attachments=data.get("attachments", []),
        )
