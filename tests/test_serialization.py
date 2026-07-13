"""Tests for model serialization via to_dict() and json.dumps()."""

import json

from letmesendemail import SendAttachment
from letmesendemail._models import (
    ContactCategoryItem,
    ContactCategoryListResponse,
    ContactItem,
    ContactListResponse,
    ContactUpdateResponse,
    DomainItem,
    DomainListResponse,
    EmailAttachment,
    EmailListItem,
    EmailListResponse,
    EmailTopicItem,
    EmailTopicListResponse,
    PaginationInfo,
    Recipient,
    SendEmailResponse,
    ShowEmailResponse,
    StatusResponse,
    VerifyEmailResponse,
)


def test_send_attachment_is_plain_json_serializable_dict() -> None:
    attachment: SendAttachment = {
        "name": "report.pdf",
        "content": "cGRmLWNvbnRlbnQ=",
        "mime": "application/pdf",
        "content_disposition": "attachment",
    }

    parsed = json.loads(json.dumps(attachment))

    assert parsed == attachment


def test_send_email_response_to_dict() -> None:
    resp = SendEmailResponse(
        id="e1", status="accepted", emails=["j@e.com"], restricted_emails=[], duplicate=False
    )
    d = resp.to_dict()
    assert d["id"] == "e1"
    assert d["status"] == "accepted"
    assert d["emails"] == ["j@e.com"]
    assert d["duplicate"] is False


def test_verify_email_response_to_dict() -> None:
    resp = VerifyEmailResponse(
        email="j@e.com",
        score=85,
        status="valid",
        domain_exists=True,
        disposable=False,
        valid_syntax=True,
        belongs_to="gmail.com",
    )
    d = resp.to_dict()
    assert d["score"] == 85
    assert d["belongs_to"] == "gmail.com"
    assert d["disposable"] is False


def test_email_list_item_to_dict() -> None:
    item = EmailListItem(
        id="e1",
        status="sent",
        subject="Hello",
        event_name=None,
        type="transactional",
        created_at="2026-01-01T00:00:00Z",
        sent_at=None,
        recipients_count=1,
        attachments_count=0,
    )
    d = item.to_dict()
    assert d["id"] == "e1"
    assert d["subject"] == "Hello"
    assert d["sent_at"] is None


def test_email_list_response_to_dict() -> None:
    item = EmailListItem(
        id="e1",
        status="sent",
        subject="Hi",
        type="tx",
        created_at="2026-01-01T00:00:00Z",
        recipients_count=1,
        attachments_count=0,
    )
    pagination = PaginationInfo(has_more=False, per_page=10, fetched=1, total=1)
    resp = EmailListResponse(data=[item], pagination=pagination)
    d = resp.to_dict()
    assert len(d["data"]) == 1
    assert d["data"][0]["id"] == "e1"
    assert d["pagination"]["has_more"] is False
    assert d["pagination"]["total"] == 1


def test_show_email_response_nested() -> None:
    recipient = Recipient(
        type="to",
        status="sent",
        email_address="u@e.com",
        is_suppressed=False,
        open_count=1,
        click_count=0,
    )
    attachment = EmailAttachment(
        id="a1", name="doc.pdf", mime="application/pdf", size=1234, download_url="https://..."
    )
    resp = ShowEmailResponse(
        id="e1",
        status="sent",
        subject="Test",
        type="tx",
        created_at="2026-01-01T00:00:00Z",
        recipients_count=1,
        attachments_count=1,
        recipients=[recipient],
        attachments=[attachment],
    )
    d = resp.to_dict()
    assert len(d["recipients"]) == 1
    assert d["recipients"][0]["email_address"] == "u@e.com"
    assert d["recipients"][0]["open_count"] == 1
    assert len(d["attachments"]) == 1
    assert d["attachments"][0]["size"] == 1234
    assert d["attachments"][0]["download_url"] == "https://..."


def test_pagination_info_to_dict() -> None:
    p = PaginationInfo(has_more=True, per_page=20, fetched=5, total=100)
    d = p.to_dict()
    assert d["has_more"] is True
    assert d["per_page"] == 20
    assert d["total"] == 100


def test_domain_item_to_dict() -> None:
    d = DomainItem(
        id="d1", domain_name="example.com", status="verified", created_at="2026-01-01T00:00:00Z"
    ).to_dict()
    assert d["domain_name"] == "example.com"


def test_domain_list_response_to_dict() -> None:
    item = DomainItem(
        id="d1", domain_name="example.com", status="verified", created_at="2026-01-01T00:00:00Z"
    )
    pagination = PaginationInfo(has_more=False, per_page=20, fetched=1, total=1)
    resp = DomainListResponse(data=[item], pagination=pagination)
    d = resp.to_dict()
    assert len(d["data"]) == 1


def test_contact_item_to_dict() -> None:
    c = ContactItem(
        id="c1",
        email="j@e.com",
        first_name="John",
        is_globally_unsubscribed=False,
        created_at="2026-01-01T00:00:00Z",
    )
    d = c.to_dict()
    assert d["email"] == "j@e.com"
    assert d["first_name"] == "John"
    assert d["is_globally_unsubscribed"] is False


def test_contact_update_response_to_dict() -> None:
    d = ContactUpdateResponse(id="c1").to_dict()
    assert d["id"] == "c1"


def test_contact_list_response_to_dict() -> None:
    item = ContactItem(id="c1", email="j@e.com", created_at="2026-01-01T00:00:00Z")
    pagination = PaginationInfo(has_more=False, per_page=20, fetched=1, total=1)
    resp = ContactListResponse(data=[item], pagination=pagination)
    d = resp.to_dict()
    assert len(d["data"]) == 1


def test_contact_category_item_to_dict() -> None:
    d = ContactCategoryItem(id="cat1", name="VIP", slug="vip").to_dict()
    assert d["slug"] == "vip"


def test_contact_category_list_response_to_dict() -> None:
    item = ContactCategoryItem(id="cat1", name="VIP", slug="vip")
    pagination = PaginationInfo(has_more=False, per_page=20, fetched=1, total=1)
    resp = ContactCategoryListResponse(data=[item], pagination=pagination)
    d = resp.to_dict()
    assert len(d["data"]) == 1


def test_email_topic_item_to_dict() -> None:
    t = EmailTopicItem(
        id="t1",
        name="Updates",
        slug="updates",
        description="Product updates",
        auto_subscribe=True,
        public=False,
        created_at="2026-01-01T00:00:00Z",
    )
    d = t.to_dict()
    assert d["name"] == "Updates"
    assert d["auto_subscribe"] is True


def test_email_topic_list_response_to_dict() -> None:
    item = EmailTopicItem(
        id="t1", name="Updates", slug="updates", created_at="2026-01-01T00:00:00Z"
    )
    pagination = PaginationInfo(has_more=False, per_page=20, fetched=1, total=1)
    resp = EmailTopicListResponse(data=[item], pagination=pagination)
    d = resp.to_dict()
    assert len(d["data"]) == 1


def test_status_response_to_dict() -> None:
    s = StatusResponse(status="deleted", message="Ok")
    d = s.to_dict()
    assert d["status"] == "deleted"
    assert d["message"] == "Ok"


def test_status_response_no_message() -> None:
    s = StatusResponse(status="deleted")
    d = s.to_dict()
    assert d["status"] == "deleted"
    assert d.get("message") is None


def test_recipient_full_fields() -> None:
    r = Recipient(
        type="to",
        status="sent",
        email_address="u@e.com",
        bounce_type="permanent",
        bounce_reason="mailbox full",
        is_suppressed=False,
        open_count=1,
        click_count=0,
        error_message="550 5.1.1",
        delivered_at="2026-01-01T00:00:00Z",
    )
    d = r.to_dict()
    assert d["bounce_reason"] == "mailbox full"
    assert d["open_count"] == 1
    assert d["delivered_at"] == "2026-01-01T00:00:00Z"


def test_email_attachment_full_fields() -> None:
    a = EmailAttachment(
        id="a1",
        name="rpt.pdf",
        mime="application/pdf",
        content_id="cid123",
        content_disposition="inline",
        size=999,
        download_url="https://dl.example.com/rpt.pdf",
    )
    d = a.to_dict()
    assert d["content_id"] == "cid123"
    assert d["download_url"] == "https://dl.example.com/rpt.pdf"


def test_json_serialization() -> None:
    """to_dict() output should be consumable by json.dumps/loads."""
    resp = SendEmailResponse(
        id="e1", status="accepted", emails=["j@e.com"], restricted_emails=[], duplicate=True
    )
    d = resp.to_dict()
    json_str = json.dumps(d)
    parsed = json.loads(json_str)
    assert parsed["duplicate"] is True
    assert parsed["id"] == "e1"


def test_defensive_copy() -> None:
    resp = SendEmailResponse(id="e1", status="sent", emails=[], restricted_emails=[])
    d = resp.to_dict()
    d["id"] = "modified"
    assert resp.id == "e1"


def test_null_values() -> None:
    item = EmailListItem(
        id="e1",
        status="sent",
        subject=None,
        event_name=None,
        type="tx",
        created_at="2026-01-01T00:00:00Z",
        sent_at=None,
        recipients_count=0,
        attachments_count=0,
    )
    d = item.to_dict()
    assert d["subject"] is None
    assert d["event_name"] is None
    assert d["sent_at"] is None


def test_boolean_values() -> None:
    resp = SendEmailResponse(
        id="e1", status="sent", emails=[], restricted_emails=[], duplicate=True
    )
    d = resp.to_dict()
    assert d["duplicate"] is True
    assert isinstance(d["duplicate"], bool)


def test_numeric_values() -> None:
    p = PaginationInfo(has_more=True, per_page=25, fetched=10, total=1000)
    d = p.to_dict()
    assert isinstance(d["per_page"], int)
    assert isinstance(d["total"], int)
