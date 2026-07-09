from letmesendemail import LetMeSendEmail

CREATE_FIXTURE = {
    "id": "01kvtsgfb2rp5g1y3xdsrnk6n4",
    "name": "Product Updates",
    "slug": "product-updates",
    "description": "Emails for product updates",
    "auto_subscribe": True,
    "public": True,
    "created_at": "2026-06-23T17:47:35.000+00:00",
    "domain": {"id": "01kvtsgfavkx5609jd3j2t6jr1", "name": "blcmiller.com"},
}

DELETE_FIXTURE = {"status": "success", "message": "Email category deleted"}


class TestEmailTopicsResource:
    def test_create(self, httpx_mock):
        httpx_mock.add_response(json=CREATE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.email_topics.create(
            name="Product Updates",
            slug="product-updates",
            description="Emails for product updates",
            auto_subscribe=True,
            public=True,
        )

        assert resp.id == CREATE_FIXTURE["id"]
        assert resp.name == CREATE_FIXTURE["name"]
        assert resp.slug == CREATE_FIXTURE["slug"]
        assert resp.auto_subscribe is True
        assert resp.public is True

    def test_delete(self, httpx_mock):
        httpx_mock.add_response(json=DELETE_FIXTURE)
        client = LetMeSendEmail(api_key="test")

        resp = client.email_topics.delete("01kvtsgfdq4xw54vcvqw0ae68n")

        assert resp.status == DELETE_FIXTURE["status"]
        assert resp.message == DELETE_FIXTURE["message"]
