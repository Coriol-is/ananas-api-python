"""Synchronous Ananas API client."""

from __future__ import annotations

import time
from types import TracebackType
from typing import Any, Optional, Type, Union

import httpx

from .errors import AnanasAPIError, AnanasAuthenticationError

JSON = Union[dict[str, Any], list[Any], str, int, float, bool, None]


class AnanasClient:
    """A synchronous client for the Ananas merchant API."""

    TOKEN_PATH = "/iam/api/v1/auth/token"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        scope: str = "public_api/full_access",
        timeout: Union[float, httpx.Timeout] = 30.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url must not be empty")
        credentials = (api_key, client_id, client_secret)
        if not access_token and not all(credentials):
            raise ValueError(
                "provide access_token or all of api_key, client_id, and client_secret"
            )

        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self._access_token = access_token
        self._token_expires_at: Optional[float] = None
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=base_url.rstrip("/"), timeout=timeout
        )

    def __enter__(self) -> "AnanasClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the internally managed HTTP client."""
        if self._owns_client:
            self._client.close()

    def authenticate(self) -> str:
        """Request and cache a bearer token using client credentials."""
        if not all((self.api_key, self.client_id, self.client_secret)):
            raise ValueError("client credentials are required to request a token")

        response = self._client.post(
            self.TOKEN_PATH,
            headers={"X-API-Key": self.api_key},
            json={
                "grantType": "CLIENT_CREDENTIALS",
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "scope": self.scope,
            },
        )
        if not response.is_success:
            raise AnanasAuthenticationError(response)

        payload = response.json()
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise AnanasAuthenticationError(response)

        expires_in = payload.get("expires_in", 0)
        self._access_token = token
        if isinstance(expires_in, (int, float)) and expires_in > 0:
            self._token_expires_at = time.monotonic() + max(0, expires_in - 30)
        else:
            self._token_expires_at = None
        return token

    def request(self, method: str, path: str, **kwargs: Any) -> JSON:
        """Send an authenticated request and return its decoded response body."""
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("Accept", "application/json")
        headers["Authorization"] = f"Bearer {self._valid_access_token()}"

        response = self._client.request(method, path, headers=headers, **kwargs)
        if not response.is_success:
            raise AnanasAPIError(response)
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, path: str, **kwargs: Any) -> JSON:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> JSON:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> JSON:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> JSON:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> JSON:
        return self.request("DELETE", path, **kwargs)

    def _valid_access_token(self) -> str:
        if self._access_token and (
            self._token_expires_at is None or time.monotonic() < self._token_expires_at
        ):
            return self._access_token
        return self.authenticate()
