import httpx
import pytest
from letmesendemail import LetMeSendEmail

CREATE_FIXTURE = {
    "id": "01kvtsch6t80qpx3ncfea2r5a3",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "11231231234",
    "is_globally_unsubscribed": False,
    "created_at": "2026-06-23T17:45:26.000+00:00",
    "categories": [
        {"id": "c1", "name": "ea labore omnis", "slug": "ea-labore-omnis"}
    ],
}

UPDATE_FIXTURE = {"id": "01kvtsch98rxyxwaxwx2fbpsbp"}

DELETE_FIXTURE = {"status": "success"}


class TestContactsResource:
    def test_create(self, httpx_mock):
        httpx_mock.add_response(json=CREATE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.contacts.create(email="john@example.com")

        assert resp.id == CREATE_FIXTURE["id"]
        assert resp.email == CREATE_FIXTURE["email"]
        assert resp.first_name == "John"
        assert resp.last_name == "Doe"

    def test_update(self, httpx_mock):
        httpx_mock.add_response(json=UPDATE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.contacts.update(id="01kvtsch98rxyxwaxwx2fbpsbp", first_name="Jane")

        assert resp.id == UPDATE_FIXTURE["id"]

    def test_delete(self, httpx_mock):
        httpx_mock.add_response(json=DELETE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.contacts.delete("01kvtscham9bjdwftnxxa8at1k")

        assert resp.status == DELETE_FIXTURE["status"]
