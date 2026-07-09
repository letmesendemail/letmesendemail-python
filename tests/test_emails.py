import httpx
import pytest
from letmesendemail import LetMeSendEmail

SEND_FIXTURE = {
    "id": "01kvv5a6xk9qd6y2egeae8w76e",
    "status": "pending_scan",
    "emails": ["john@example.com", "jane@example.com", "jim@example.com"],
    "restricted_emails": [],
}

VERIFY_FIXTURE = {
    "email": "john+doe@gmail.com",
    "score": 40,
    "status": "valid",
    "domain_exists": True,
    "disposable": False,
    "role_based": False,
    "has_mailbox": True,
    "receive_email": True,
    "mx_records": True,
    "valid_syntax": True,
    "belongs_to": "john@gmail.com",
}

LIST_FIXTURE = {
    "data": [
        {
            "id": "01kvtb8c6xh94vdsh633t8m83r",
            "status": "queued",
            "subject": "Eos autem ducimus soluta hic at est ipsam.",
            "event_name": None,
            "type": "broadcast",
            "created_at": "2026-06-23T13:38:30.000+00:00",
            "sent_at": None,
            "recipients_count": 1,
            "attachments_count": 0,
        },
    ],
    "pagination": {"has_more": True, "per_page": 2, "fetched": 1, "total": 100},
}

SHOW_FIXTURE = {
    "id": "01kvv5dv472evp42a60sy4p7zx",
    "status": "sent",
    "subject": "Et et earum et omnis.",
    "event_name": None,
    "type": "transactional",
    "created_at": "2026-06-23T21:15:52.000+00:00",
    "sent_at": None,
    "recipients_count": 1,
    "attachments_count": 0,
    "recipients": [
        {
            "type": "to",
            "status": "queued",
            "email_address": "koelpin.burdette@example.org",
            "bounce_type": None,
            "bounce_reason": None,
            "bounced_at": None,
            "complaint_type": None,
            "complained_at": None,
            "is_suppressed": False,
            "suppression_reason": None,
            "opened_at": None,
            "open_count": 0,
            "clicked_at": None,
            "click_count": 0,
            "failed_at": None,
            "error_message": None,
            "delivered_at": None,
            "sent_at": None,
        }
    ],
    "attachments": [
        {
            "id": "01kvv5dv461r4x1za05c0sy6nq",
            "name": "I9wJnL1QeUOKnsgE.png",
            "mime": "image/png",
            "content_id": "XUT5SWQt5AsAsRVv",
            "content_disposition": "attachment",
            "size": 16174079,
            "download_url": "https://letmesend.email/files/...",
        }
    ],
}


class TestEmailsResource:
    def test_send(self, httpx_mock):
        httpx_mock.add_response(json=SEND_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.emails.send(
            from_="Acme <hello@acme.com>",
            to=["person@example.com"],
            subject="Welcome",
            html="<p>Hello</p>",
        )

        assert resp.id == SEND_FIXTURE["id"]
        assert resp.status == SEND_FIXTURE["status"]
        assert resp.emails == SEND_FIXTURE["emails"]
        assert resp.restricted_emails == SEND_FIXTURE["restricted_emails"]
        assert resp.duplicate is False

    def test_verify(self, httpx_mock):
        httpx_mock.add_response(json=VERIFY_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.emails.verify("john+doe@gmail.com")

        assert resp.email == VERIFY_FIXTURE["email"]
        assert resp.score == VERIFY_FIXTURE["score"]
        assert resp.status == VERIFY_FIXTURE["status"]
        assert resp.domain_exists is True
        assert resp.disposable is False
        assert resp.has_mailbox is True
        assert resp.belongs_to == "john@gmail.com"

    def test_list(self, httpx_mock):
        httpx_mock.add_response(json=LIST_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.emails.list()

        assert len(resp.data) == 1
        assert resp.data[0].id == LIST_FIXTURE["data"][0]["id"]
        assert resp.data[0].subject == LIST_FIXTURE["data"][0]["subject"]
        assert resp.pagination.has_more is True
        assert resp.pagination.total == 100

    def test_get(self, httpx_mock):
        httpx_mock.add_response(json=SHOW_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.emails.get("01kvv5dv472evp42a60sy4p7zx")

        assert resp.id == SHOW_FIXTURE["id"]
        assert resp.status == SHOW_FIXTURE["status"]
        assert resp.subject == SHOW_FIXTURE["subject"]
        assert resp.recipients_count == 1
        assert resp.attachments_count == 0
