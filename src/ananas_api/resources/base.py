"""Shared helpers for endpoint resource classes."""

from __future__ import annotations

from typing import Any, Generic, Protocol, Type, TypeVar, Union

from pydantic import BaseModel, TypeAdapter

JSON = Union[dict[str, Any], list[Any], str, int, float, bool, None]
ModelT = TypeVar("ModelT", bound=BaseModel)
ValueT = TypeVar("ValueT")


class Requester(Protocol):
    def request(self, method: str, path: str, **kwargs: Any) -> JSON: ...


class Resource:
    """Base resource backed by an authenticated Ananas client."""

    def __init__(self, client: Requester) -> None:
        self._client = client

    def _request_model(self, model: Type[ModelT], method: str, path: str, **kwargs: Any) -> ModelT:
        return model.model_validate(self._client.request(method, path, **kwargs))

    def _request_as(
        self, annotation: Type[ValueT], method: str, path: str, **kwargs: Any
    ) -> ValueT:
        return TypeAdapter(annotation).validate_python(self._client.request(method, path, **kwargs))


class Page(Generic[ValueT]):
    """A page returned by a page-number based endpoint."""

    def __init__(self, items: list[ValueT], number: int, size: int) -> None:
        self.items = items
        self.number = number
        self.size = size

    @property
    def has_next(self) -> bool:
        return len(self.items) >= self.size
