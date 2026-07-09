from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PaginationInfo:
    has_more: bool = False
    per_page: int = 0
    fetched: int = 0
    total: int = 0


@dataclass
class SendEmailResponse:
    id: str = ""
    status: str = ""
    emails: list[str] = field(default_factory=list)
    restricted_emails: list[str] = field(default_factory=list)
    duplicate: bool = False


@dataclass
class VerifyEmailResponse:
    email: str = ""
    score: int = 0
    status: str = ""
    domain_exists: bool = False
    disposable: bool = False
    role_based: bool = False
    has_mailbox: bool = False
    receive_email: bool = False
    mx_records: bool = False
    valid_syntax: bool = False
    belongs_to: str | None = None


@dataclass
class EmailListItem:
    id: str = ""
    status: str = ""
    subject: str | None = None
    event_name: str | None = None
    type: str = ""
    created_at: str = ""
    sent_at: str | None = None
    recipients_count: int = 0
    attachments_count: int = 0


@dataclass
class EmailListResponse:
    data: list[EmailListItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


@dataclass
class Recipient:
    type: str = ""
    status: str = ""
    email_address: str = ""
    bounce_type: str | None = None
    bounce_reason: str | None = None
    bounced_at: str | None = None
    complaint_type: str | None = None
    complained_at: str | None = None
    is_suppressed: bool = False
    suppression_reason: str | None = None
    opened_at: str | None = None
    open_count: int = 0
    clicked_at: str | None = None
    click_count: int = 0
    failed_at: str | None = None
    error_message: str | None = None
    delivered_at: str | None = None
    sent_at: str | None = None


@dataclass
class EmailAttachment:
    id: str = ""
    name: str = ""
    mime: str = ""
    content_id: str = ""
    content_disposition: str = ""
    size: int = 0
    download_url: str = ""


@dataclass
class ShowEmailResponse:
    id: str = ""
    status: str = ""
    subject: str | None = None
    event_name: str | None = None
    type: str = ""
    created_at: str = ""
    sent_at: str | None = None
    recipients_count: int = 0
    attachments_count: int = 0
    recipients: list[Recipient] = field(default_factory=list)
    attachments: list[EmailAttachment] = field(default_factory=list)


@dataclass
class DomainItem:
    id: str = ""
    domain_name: str = ""
    status: str = ""
    created_at: str = ""


@dataclass
class DomainListResponse:
    data: list[DomainItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


@dataclass
class StatusResponse:
    status: str = ""
    message: str | None = None


@dataclass
class ContactItem:
    id: str = ""
    email: str = ""
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_globally_unsubscribed: bool = False
    created_at: str = ""
    categories: list[dict[str, Any]] = field(default_factory=list)
    email_topics: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ContactListResponse:
    data: list[ContactItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


@dataclass
class ContactCategoryItem:
    id: str = ""
    name: str = ""
    slug: str = ""


@dataclass
class ContactCategoryListResponse:
    data: list[ContactCategoryItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


@dataclass
class EmailTopicItem:
    id: str = ""
    name: str = ""
    slug: str = ""
    description: str | None = None
    auto_subscribe: bool = False
    public: bool = False
    created_at: str = ""
    domain: dict[str, Any] | None = None


@dataclass
class EmailTopicListResponse:
    data: list[EmailTopicItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)
