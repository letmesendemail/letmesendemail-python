from __future__ import annotations

from typing import Any

import httpx

from letmesendemail._config import ClientConfig
from letmesendemail._errors import NetworkError, TimeoutError, _error_from_response
from letmesendemail.resources.contact_categories import ContactCategoriesResource
from letmesendemail.resources.contacts import ContactsResource
from letmesendemail.resources.domains import DomainsResource
from letmesendemail.resources.email_topics import EmailTopicsResource
from letmesendemail.resources.emails import EmailsResource

__version__ = "0.1.0"


class LetMeSendEmail:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout_ms: int | None = None,
        retries: int | None = None,
        _client: httpx.Client | None = None,
    ) -> None:
        if api_key is None:
            raise ValueError("api_key is required")
        self._config = ClientConfig(
            api_key=api_key,
            base_url=base_url or ClientConfig.base_url,
            timeout_ms=timeout_ms or ClientConfig.timeout_ms,
            retries=retries or ClientConfig.retries,
        )
        self._http = _client or httpx.Client(timeout=httpx.Timeout(self._config.timeout_ms / 1000))

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._config.base_url}/{path.lstrip('/')}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"letmesendemail-python/{__version__}",
        }
        if extra_headers:
            headers.update(extra_headers)

        try:
            response = self._http.request(method, url, json=body, headers=headers)
        except httpx.ConnectError as e:
            raise NetworkError(str(e)) from e
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timed out.") from e

        response_headers: dict[str, str] = {}
        for key, val in response.headers.items():
            response_headers[key.lower()] = val

        if response.status_code >= 400:
            try:
                resp_body = response.json()
            except Exception:
                resp_body = {}
            raise _error_from_response(response.status_code, resp_body, response_headers)

        return response.json()

    @property
    def emails(self) -> EmailsResource:
        return EmailsResource(self._request)

    @property
    def domains(self) -> DomainsResource:
        return DomainsResource(self._request)

    @property
    def contacts(self) -> ContactsResource:
        return ContactsResource(self._request)

    @property
    def contact_categories(self) -> ContactCategoriesResource:
        return ContactCategoriesResource(self._request)

    @property
    def email_topics(self) -> EmailTopicsResource:
        return EmailTopicsResource(self._request)
