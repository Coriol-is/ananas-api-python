import json

import httpx
import pytest
from pydantic import ValidationError

from ananas_api import AnanasClient
from ananas_api.models.products import (
    CheckIfEANExistsRequest,
    PackageWeightUnit,
    ProductRequest,
    UpdateProductRequest,
)
from ananas_api.resources.products import ProductsResource


def resource(handler):
    http = httpx.Client(base_url="https://api.test", transport=httpx.MockTransport(handler))
    return ProductsResource(
        AnanasClient(base_url="https://api.test", access_token="token", http_client=http)
    )


def test_get_products_uses_filters_and_returns_models() -> None:
    def handler(request):
        assert request.url.path.endswith("/products")
        assert request.url.params["date-modified-after"] == "2026-01-01"
        assert request.url.params["search"] == "phone"
        return httpx.Response(200, json=[{"id": 1, "ananasCode": "A1"}], request=request)

    result = resource(handler).get_products(search="phone", date_modified_after="2026-01-01")
    assert result[0].id == 1
    assert result[0].ananas_code == "A1"


def test_get_basic_products_and_constraints() -> None:
    def handler(request):
        return httpx.Response(
            200, json=[{"id": 2, "warehouse": "MERCHANT_WAREHOUSE"}], request=request
        )

    products = resource(handler)
    assert products.get_basic_products(size=2500)[0].warehouse.value == "MERCHANT_WAREHOUSE"
    with pytest.raises(ValueError, match="2500"):
        products.get_basic_products(size=2501)
    with pytest.raises(ValueError, match="page"):
        products.get_products(page=-1)


def test_product_pagination_stops_on_short_page() -> None:
    pages = []

    def handler(request):
        page = int(request.url.params["page"])
        pages.append(page)
        count = 2 if page == 0 else 1
        return httpx.Response(
            200, json=[{"id": page * 2 + i} for i in range(count)], request=request
        )

    assert [item.id for item in resource(handler).iter_products(size=2)] == [0, 1, 2]
    assert pages == [0, 1]


def test_basic_product_pagination_stops_on_empty_page() -> None:
    def handler(request):
        page = int(request.url.params["page"])
        body = [{"id": 1}] if page == 0 else []
        return httpx.Response(200, json=body, request=request)

    assert [item.id for item in resource(handler).iter_basic_products(size=1)] == [1]


def test_import_or_update_products_serializes_aliases() -> None:
    def handler(request):
        assert request.method == "POST"
        assert json.loads(request.content) == {
            "name": "Phone",
            "packageWeightUnit": "KG",
            "basePrice": 100.0,
        }
        return httpx.Response(200, json={"id": "progress-1"}, request=request)

    result = resource(handler).import_or_update_products(
        ProductRequest(name="Phone", base_price=100)
    )
    assert result.id == "progress-1"


def test_update_products_returns_each_operation_result() -> None:
    def handler(request):
        body = json.loads(request.content)
        assert request.method == "PUT"
        assert body[0]["packageWeightUnit"] == "G"
        return httpx.Response(
            200, json=[{"status": "SUCCESS", "errors": [], "myProductId": 7}], request=request
        )

    result = resource(handler).update_products(
        [UpdateProductRequest(id=7, package_weight_unit=PackageWeightUnit.G)]
    )
    assert result[0].my_product_id == 7


def test_update_single_product_validates_id_and_parses_result() -> None:
    products = resource(
        lambda request: httpx.Response(
            200, json={"status": "SUCCESS", "myProductId": 9}, request=request
        )
    )
    assert (
        products.update_single_product(9, UpdateProductRequest(stock_level=4)).status == "SUCCESS"
    )
    with pytest.raises(ValueError, match="greater than zero"):
        products.update_single_product(0, UpdateProductRequest())


def test_get_product_types_sets_valid_language_header() -> None:
    def handler(request):
        assert request.headers["Accept-Language"] == "en"
        return httpx.Response(200, json=["Laptop", "Phone"], request=request)

    products = resource(handler)
    assert products.get_product_types(accept_language="en") == ["Laptop", "Phone"]
    with pytest.raises(ValueError, match="accept_language"):
        products.get_product_types(accept_language="sr")


def test_check_if_ean_exists_validates_and_parses_mapping() -> None:
    def handler(request):
        assert json.loads(request.content) == ["860000000001"]
        return httpx.Response(200, json={"860000000001": True}, request=request)

    response = resource(handler).check_if_ean_exists(["860000000001"])
    assert response.root == {"860000000001": True}
    with pytest.raises(ValidationError, match="at least one EAN"):
        CheckIfEANExistsRequest([])
