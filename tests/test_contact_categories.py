import httpx
import pytest
from letmesendemail import LetMeSendEmail

CREATE_FIXTURE = {
    "id": "01kvtkm3x5tpyhyw7xcnqf32rj",
    "name": "New Name",
    "slug": "new-name",
}

LIST_FIXTURE = {
    "data": [
        {"id": "01kvtkgnwnwszdgs6w4ks0cqy3", "name": "quisquam temporibus ullam", "slug": "quisquam-temporibus-ullam"},
        {"id": "01kvtkgnwmksj0khdcbv31r2cy", "name": "nisi quam officiis", "slug": "nisi-quam-officiis"},
    ],
    "pagination": {"has_more": True, "per_page": 2, "fetched": 2, "total": 100},
}

DELETE_FIXTURE = {"status": "success"}


class TestContactCategoriesResource:
    def test_create(self, httpx_mock):
        httpx_mock.add_response(json=CREATE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.contact_categories.create(name="New Name")

        assert resp.id == CREATE_FIXTURE["id"]
        assert resp.name == CREATE_FIXTURE["name"]
        assert resp.slug == CREATE_FIXTURE["slug"]

    def test_list(self, httpx_mock):
        httpx_mock.add_response(json=LIST_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.contact_categories.list()

        assert len(resp.data) == 2
        assert resp.data[0].name == "quisquam temporibus ullam"
        assert resp.pagination.has_more is True
        assert resp.pagination.total == 100

    def test_delete(self, httpx_mock):
        httpx_mock.add_response(json=DELETE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.contact_categories.delete("01kvtmr3evcs2brxp2vcztd102")

        assert resp.status == "success"
