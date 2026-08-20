"""Reusable pagination helpers."""

from __future__ import annotations

from typing import Callable, Iterator, TypeVar

ItemT = TypeVar("ItemT")


def iterate_pages(
    fetch_page: Callable[[int, int], list[ItemT]],
    *,
    page_size: int = 100,
    start_page: int = 0,
) -> Iterator[ItemT]:
    """Yield items until a zero-based page endpoint returns a short page."""
    if page_size < 1:
        raise ValueError("page_size must be at least 1")
    if start_page < 0:
        raise ValueError("start_page must be non-negative")

    page = start_page
    while True:
        items = fetch_page(page, page_size)
        yield from items
        if len(items) < page_size:
            return
        page += 1
