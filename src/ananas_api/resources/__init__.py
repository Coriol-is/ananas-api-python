"""Named endpoint groups for the Ananas API."""

from .base import Page, Requester, Resource
from .discounts import DiscountsResource
from .payments import PaymentsResource
from .products import ProductsResource

__all__ = [
    "DiscountsResource",
    "Page",
    "PaymentsResource",
    "ProductsResource",
    "Requester",
    "Resource",
]
