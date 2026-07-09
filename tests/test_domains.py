from letmesendemail import LetMeSendEmail

LIST_FIXTURE = {
    "data": [
        {
            "id": "01kvv5tbpcaj5v9k062fr8w31e",
            "domain_name": "99xshanahan.com",
            "status": "verified",
            "created_at": "2026-06-23T21:22:42.000+00:00",
        },
    ],
    "pagination": {"has_more": False, "per_page": 20, "fetched": 1, "total": 1},
}

SHOW_FIXTURE = {
    "id": "01kvv5th65xzkwxe5avmdqbn4a",
    "domain_name": "mpxlubowitz.com",
    "status": "pending",
    "created_at": "2026-06-23T21:22:48.000+00:00",
}

VERIFY_FIXTURE = {"status": "verified"}


class TestDomainsResource:
    def test_list(self, httpx_mock):
        httpx_mock.add_response(json=LIST_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.domains.list()

        assert len(resp.data) == 1
        assert resp.data[0].domain_name == "99xshanahan.com"
        assert resp.data[0].status == "verified"
        assert resp.pagination.has_more is False

    def test_get(self, httpx_mock):
        httpx_mock.add_response(json=SHOW_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.domains.get("01kvv5th65xzkwxe5avmdqbn4a")

        assert resp.id == SHOW_FIXTURE["id"]
        assert resp.domain_name == SHOW_FIXTURE["domain_name"]
        assert resp.status == SHOW_FIXTURE["status"]

    def test_verify(self, httpx_mock):
        httpx_mock.add_response(json=VERIFY_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.domains.verify("mpxlubowitz.com")

        assert resp.status == VERIFY_FIXTURE["status"]
