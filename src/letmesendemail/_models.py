"""Response and request model dataclasses."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, TypedDict


@dataclass
class PaginationInfo:
    """Cursor-based pagination metadata."""

    has_more: bool = False
    per_page: int = 0
    fetched: int = 0
    total: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Return the pagination metadata as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the response data as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the verification result as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the email list item as a dictionary."""
        return asdict(self)


@dataclass
class EmailListResponse:
    """Paginated list of emails."""

    data: list[EmailListItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)

    def to_dict(self) -> dict[str, Any]:
        """Return the full list response as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the recipient data as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the attachment data as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the full email detail as a dictionary."""
        return asdict(self)


# ── Domains ──


@dataclass
class DomainItem:
    """A domain belonging to the account."""

    id: str = ""
    domain_name: str = ""
    status: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return the domain data as a dictionary."""
        return asdict(self)


@dataclass
class DomainListResponse:
    """Paginated list of domains."""

    data: list[DomainItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)

    def to_dict(self) -> dict[str, Any]:
        """Return the full domain list response as a dictionary."""
        return asdict(self)


@dataclass
class StatusResponse:
    """Minimal status response (delete, verify)."""

    status: str = ""
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the status response as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the contact data as a dictionary."""
        return asdict(self)


@dataclass
class ContactUpdateResponse:
    """Response from update — fixture returns only { id }."""

    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return the update response as a dictionary."""
        return asdict(self)


@dataclass
class ContactListResponse:
    """Paginated list of contacts."""

    data: list[ContactItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)

    def to_dict(self) -> dict[str, Any]:
        """Return the full contact list response as a dictionary."""
        return asdict(self)


# ── Contact Categories ──


@dataclass
class ContactCategoryItem:
    """A contact category."""

    id: str = ""
    name: str = ""
    slug: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return the category data as a dictionary."""
        return asdict(self)


@dataclass
class ContactCategoryListResponse:
    """Paginated list of contact categories."""

    data: list[ContactCategoryItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)

    def to_dict(self) -> dict[str, Any]:
        """Return the full category list response as a dictionary."""
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        """Return the topic data as a dictionary."""
        return asdict(self)


@dataclass
class EmailTopicListResponse:
    """Paginated list of email topics."""

    data: list[EmailTopicItem] = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)

    def to_dict(self) -> dict[str, Any]:
        """Return the full topic list response as a dictionary."""
        return asdict(self)
