from letmesendemail import LetMeSendEmail


class TestClient:
    def test_accepts_string_api_key(self):
        client = LetMeSendEmail(api_key="lms_live_test")
        assert client is not None

    def test_emails_resource(self):
        client = LetMeSendEmail(api_key="test")
        assert client.emails is not None

    def test_domains_resource(self):
        client = LetMeSendEmail(api_key="test")
        assert client.domains is not None

    def test_contacts_resource(self):
        client = LetMeSendEmail(api_key="test")
        assert client.contacts is not None

    def test_contact_categories_resource(self):
        client = LetMeSendEmail(api_key="test")
        assert client.contact_categories is not None

    def test_email_topics_resource(self):
        client = LetMeSendEmail(api_key="test")
        assert client.email_topics is not None

    def test_default_base_url(self):
        client = LetMeSendEmail(api_key="test")
        assert client._config.base_url == "https://letmesend.email/api/v1"

    def test_custom_base_url(self):
        client = LetMeSendEmail(api_key="test", base_url="https://custom.test/api")
        assert client._config.base_url == "https://custom.test/api"

    def test_default_timeout(self):
        client = LetMeSendEmail(api_key="test")
        assert client._config.timeout_ms == 30_000

    def test_custom_timeout(self):
        client = LetMeSendEmail(api_key="test", timeout_ms=10_000)
        assert client._config.timeout_ms == 10_000
