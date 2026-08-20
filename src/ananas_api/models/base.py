"""Shared model configuration for Ananas API payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base for typed API payloads with JSON aliases and strict validation."""

    model_config = ConfigDict(
        alias_generator=None,
        populate_by_name=True,
        extra="forbid",
        validate_assignment=True,
    )

    def to_payload(self, *, exclude_none: bool = True) -> dict[str, Any]:
        """Serialize a request model using the API's field aliases."""
        return self.model_dump(by_alias=True, exclude_none=exclude_none, mode="json")


class APIResponseModel(APIModel):
    """Base for responses, which may gain fields before the client is updated."""

    model_config = ConfigDict(
        alias_generator=None,
        populate_by_name=True,
        extra="allow",
        validate_assignment=True,
    )
