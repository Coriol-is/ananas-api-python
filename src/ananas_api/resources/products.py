"""Named operations for the Ananas Products API."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Optional, Sequence, Union

from pydantic import TypeAdapter

from ..models.products import (
    BasicProductResponse,
    CheckIfEANExistsRequest,
    CheckIfEANExistsResponse,
    ImportProductsResponse,
    ProductRequest,
    ProductResponse,
    ProductTypesResponse,
    ProductUpdateResult,
    UpdateProductRequest,
    UpdateProductsRequest,
)


class ProductsResource:
    """Products endpoints from the merchant-integration API."""

    BASE_PATH = "/product/api/v1/merchant-integration"

    def __init__(self, client: object) -> None:
        self._client = client

    def get_products(
        self,
        *,
        search: Optional[str] = None,
        ean: Optional[str] = None,
        date_modified_after: Optional[str] = None,
        page: int = 0,
        size: int = 100,
    ) -> List[ProductResponse]:
        self._validate_page(page, size)
        payload = self._client.request(
            "GET",
            f"{self.BASE_PATH}/products",
            params=self._params(search, ean, date_modified_after, page, size),
        )
        return TypeAdapter(List[ProductResponse]).validate_python(payload)

    def iter_products(self, **kwargs: object) -> Iterator[ProductResponse]:
        page = int(kwargs.pop("page", 0))
        size = int(kwargs.pop("size", 100))
        while True:
            items = self.get_products(page=page, size=size, **kwargs)
            yield from items
            if len(items) < size:
                return
            page += 1

    def get_basic_products(
        self,
        *,
        date_modified_after: Optional[str] = None,
        page: int = 0,
        size: int = 100,
    ) -> List[BasicProductResponse]:
        self._validate_page(page, size, max_size=2500)
        params = {"page": page, "size": size}
        if date_modified_after is not None:
            params["date-modified-after"] = date_modified_after
        payload = self._client.request("GET", f"{self.BASE_PATH}/basic-products", params=params)
        return TypeAdapter(List[BasicProductResponse]).validate_python(payload)

    def iter_basic_products(self, **kwargs: object) -> Iterator[BasicProductResponse]:
        page = int(kwargs.pop("page", 0))
        size = int(kwargs.pop("size", 100))
        while True:
            items = self.get_basic_products(page=page, size=size, **kwargs)
            yield from items
            if len(items) < size:
                return
            page += 1

    def import_or_update_products(self, product: ProductRequest) -> ImportProductsResponse:
        payload = self._client.request(
            "POST",
            f"{self.BASE_PATH}/import",
            json=product.model_dump(by_alias=True, exclude_none=True),
        )
        return ImportProductsResponse.model_validate(payload)

    def update_products(
        self, products: Union[UpdateProductsRequest, Sequence[UpdateProductRequest]]
    ) -> List[ProductUpdateResult]:
        request = (
            products
            if isinstance(products, UpdateProductsRequest)
            else UpdateProductsRequest(list(products))
        )
        payload = self._client.request(
            "PUT", f"{self.BASE_PATH}/product/bulk", json=request.model_dump(by_alias=True)
        )
        return TypeAdapter(List[ProductUpdateResult]).validate_python(payload)

    def update_single_product(
        self, product_id: int, product: UpdateProductRequest
    ) -> ProductUpdateResult:
        if product_id <= 0:
            raise ValueError("product_id must be greater than zero")
        payload = self._client.request(
            "PUT",
            f"{self.BASE_PATH}/product/{product_id}",
            json=product.model_dump(by_alias=True, exclude_none=True),
        )
        return ProductUpdateResult.model_validate(payload)

    def get_product_types(self, *, accept_language: Optional[str] = None) -> List[str]:
        if accept_language not in (None, "en"):
            raise ValueError("accept_language must be 'en'")
        headers = {"Accept-Language": accept_language} if accept_language else None
        payload = self._client.request("GET", f"{self.BASE_PATH}/product-type", headers=headers)
        return ProductTypesResponse.model_validate(payload).root

    # Mirrors the OpenAPI operationId ``getProductsTypes``.
    def get_products_types(self, *, accept_language: Optional[str] = None) -> List[str]:
        return self.get_product_types(accept_language=accept_language)

    def check_if_ean_exists(self, eans: Iterable[str]) -> CheckIfEANExistsResponse:
        request = CheckIfEANExistsRequest(list(eans))
        payload = self._client.request(
            "POST", f"{self.BASE_PATH}/ean/exists", json=request.model_dump()
        )
        return CheckIfEANExistsResponse.model_validate(payload)

    @staticmethod
    def _validate_page(page: int, size: int, *, max_size: Optional[int] = None) -> None:
        if page < 0:
            raise ValueError("page must be zero or greater")
        if size <= 0:
            raise ValueError("size must be greater than zero")
        if max_size is not None and size > max_size:
            raise ValueError(f"size must not exceed {max_size}")

    @staticmethod
    def _params(
        search: Optional[str],
        ean: Optional[str],
        date_modified_after: Optional[str],
        page: int,
        size: int,
    ) -> dict[str, object]:
        params: dict[str, object] = {"page": page, "size": size}
        for key, value in (
            ("search", search),
            ("ean", ean),
            ("date-modified-after", date_modified_after),
        ):
            if value is not None:
                params[key] = value
        return params
