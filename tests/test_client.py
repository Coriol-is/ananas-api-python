import httpx
import pytest

from ananas_api import AnanasAPIError, AnanasClient


def test_client_authenticates_and_sends_bearer_token() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == AnanasClient.TOKEN_PATH:
            assert request.headers["X-API-Key"] == "key"
            return httpx.Response(
                200,
                json={"access_token": "token", "expires_in": 3600},
                request=request,
            )
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"ok": True}, request=request)

    http = httpx.Client(base_url="https://api.example.test", transport=httpx.MockTransport(handler))
    client = AnanasClient(
        base_url="https://api.example.test",
        api_key="key",
        client_id="id",
        client_secret="secret",
        http_client=http,
    )

    assert client.get("/products") == {"ok": True}
    assert len(requests) == 2


def test_existing_token_skips_authentication() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer existing"
        return httpx.Response(204, request=request)

    http = httpx.Client(base_url="https://api.example.test", transport=httpx.MockTransport(handler))
    client = AnanasClient(
        base_url="https://api.example.test", access_token="existing", http_client=http
    )

    assert client.delete("/products/1") is None


def test_api_errors_include_status_and_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"message": "Invalid request"}, request=request)

    http = httpx.Client(base_url="https://api.example.test", transport=httpx.MockTransport(handler))
    client = AnanasClient(
        base_url="https://api.example.test", access_token="token", http_client=http
    )

    with pytest.raises(AnanasAPIError, match="Invalid request") as raised:
        client.get("/products")

    assert raised.value.status_code == 400
    assert raised.value.body == {"message": "Invalid request"}


def test_credentials_are_required() -> None:
    with pytest.raises(ValueError, match="provide access_token"):
        AnanasClient(base_url="https://api.example.test")
