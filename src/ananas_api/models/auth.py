"""Authentication request and response models."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from .base import APIModel, APIResponseModel


class TokenRequest(APIModel):
    grant_type: Literal["CLIENT_CREDENTIALS"] = Field(
        default="CLIENT_CREDENTIALS", alias="grantType"
    )
    client_id: str = Field(min_length=1, alias="clientId")
    client_secret: str = Field(min_length=1, alias="clientSecret")
    scope: str = Field(default="public_api/full_access", min_length=1)


class TokenResponse(APIResponseModel):
    id_token: Optional[str] = None
    access_token: str = Field(min_length=1)
    refresh_token: Optional[str] = None
    expires_in: int = Field(ge=0)
    token_type: Literal["Bearer"] = "Bearer"
