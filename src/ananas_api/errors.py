"""Exceptions raised by the Ananas API client."""

from __future__ import annotations

from typing import Any, Optional

import httpx


class AnanasAPIError(Exception):
    """An unsuccessful response returned by the Ananas API."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.status_code = response.status_code
        try:
            self.body: Any = response.json()
        except ValueError:
            self.body = response.text

        message: Optional[str] = None
        if isinstance(self.body, dict):
            value = self.body.get("message")
            if isinstance(value, str):
                message = value
        super().__init__(message or f"Ananas API returned HTTP {self.status_code}")


class AnanasAuthenticationError(AnanasAPIError):
    """Authentication with the Ananas API failed."""

