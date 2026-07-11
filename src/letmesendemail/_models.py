"""Response and request model dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict


@dataclass
class PaginationInfo:
    """Cursor-based pagination metadata."""

    has_more: bool = False
    per_page: int = 0
    fetched: int = 0
    total: int = 0


# ── Attachment request types ──


class SendAttachmentRequired(TypedDict):
    """Required fields for a request attachment."""

    name: str


class SendAttachment(SendAttachmentRequired, total=False):
    """Request attachment. Provide either `path` (URL) or `content` (base64)."""

    path: str
    content: str
    mime: str
    content_id: str
    content_disposition: str


# ── Emails ──


@dataclass
class SendEmailResponse:
    """Response from sending (or idempotently re-sending) an email."""

    id: str = ""
    status: str = ""
    emails: list[str] = field(default_factory=list)
    restricted_emails: list[str] = field(default_factory=list)
    duplicate: bool = False


@dataclass
class VerifyEmailResponse:
    """Result of verifying an email address."""

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
    """One email in a list response."""

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
    """Paginated list of emails."""

    data: list[EmailListItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


@dataclass
class Recipient:
    """A single recipient of an email."""

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
    """An attachment on a sent email."""

    id: str = ""
    name: str = ""
    mime: str = ""
    content_id: str = ""
    content_disposition: str = ""
    size: int = 0
    download_url: str = ""


@dataclass
class ShowEmailResponse:
    """Full detail for a single email."""

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


# ── Domains ──


@dataclass
class DomainItem:
    """A domain belonging to the account."""

    id: str = ""
    domain_name: str = ""
    status: str = ""
    created_at: str = ""


@dataclass
class DomainListResponse:
    """Paginated list of domains."""

    data: list[DomainItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


@dataclass
class StatusResponse:
    """Minimal status response (delete, verify)."""

    status: str = ""
    message: str | None = None


# ── Contacts ──


@dataclass
class ContactItem:
    """A contact record."""

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
class ContactUpdateResponse:
    """Response from update — fixture returns only { id }."""

    id: str = ""


@dataclass
class ContactListResponse:
    """Paginated list of contacts."""

    data: list[ContactItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


# ── Contact Categories ──


@dataclass
class ContactCategoryItem:
    """A contact category."""

    id: str = ""
    name: str = ""
    slug: str = ""


@dataclass
class ContactCategoryListResponse:
    """Paginated list of contact categories."""

    data: list[ContactCategoryItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)


# ── Email Topics ──


@dataclass
class EmailTopicItem:
    """An email topic."""

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
    """Paginated list of email topics."""

    data: list[EmailTopicItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)
