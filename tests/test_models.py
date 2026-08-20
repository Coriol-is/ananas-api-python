import pytest
from pydantic import ValidationError

from ananas_api.models import TokenRequest, TokenResponse
from ananas_api.pagination import iterate_pages


def test_token_request_uses_openapi_aliases() -> None:
    request = TokenRequest(clientId="client", clientSecret="secret")

    assert request.to_payload() == {
        "grantType": "CLIENT_CREDENTIALS",
        "clientId": "client",
        "clientSecret": "secret",
        "scope": "public_api/full_access",
    }


def test_token_response_validates_required_access_token() -> None:
    with pytest.raises(ValidationError):
        TokenResponse.model_validate({"expires_in": 60, "token_type": "Bearer"})


def test_iterate_pages_stops_after_short_page() -> None:
    calls = []

    def fetch(page: int, size: int) -> list[int]:
        calls.append((page, size))
        return [page * size + index for index in range(size if page == 1 else 1)]

    assert list(iterate_pages(fetch, page_size=2, start_page=1)) == [2, 3, 4]
    assert calls == [(1, 2), (2, 2)]


def test_iterate_pages_validates_arguments() -> None:
    with pytest.raises(ValueError, match="page_size"):
        list(iterate_pages(lambda page, size: [], page_size=0))
