from datetime import date, datetime

import httpx
import pytest
from pydantic import ValidationError

from ananas_api.client import AnanasClient
from ananas_api.models.discounts import (
    DiscountType,
    ScheduleDiscount,
    ScheduleDiscountsRequest,
    UpdateDiscount,
    UpdateDiscountsRequest,
)
from ananas_api.resources.discounts import DiscountsResource


def resource_for(handler):
    http_client = httpx.Client(
        base_url="https://api.example.test", transport=httpx.MockTransport(handler)
    )
    client = AnanasClient(
        base_url="https://api.example.test", access_token="token", http_client=http_client
    )
    return DiscountsResource(client)


def test_schedule_discounts_in_bulk_serializes_aliases_and_parses_result():
    def handler(request):
        assert request.method == "POST"
        assert request.url.path == "/payment/api/v1/merchant-integration/discounts"
        assert request.read()
        assert request.headers["authorization"] == "Bearer token"
        assert request.content == (
            b'{"discounts":[{"merchantInventoryId":1194,"discountPrice":800.0,'
            b'"discountPriceCurrency":"RSD","dateFrom":"22/07/2022",'
            b'"dateTo":"29/07/2022","discountType":"SALE"}]}'
        )
        return httpx.Response(
            200,
            json={
                "scheduleResult": [
                    {
                        "success": True,
                        "data": {"merchantInventoryId": 1194, "discountId": "discount-1"},
                    }
                ]
            },
        )

    result = resource_for(handler).schedule_discounts_in_bulk(
        ScheduleDiscountsRequest(
            discounts=[
                ScheduleDiscount(
                    merchant_inventory_id=1194,
                    discount_price=800,
                    discount_price_currency="RSD",
                    date_from="22/07/2022",
                    date_to="29/07/2022",
                    discount_type=DiscountType.SALE,
                )
            ]
        )
    )
    assert result.schedule_result[0].data.discount_id == "discount-1"


def test_update_discounts_in_bulk_returns_typed_error_result():
    def handler(request):
        assert request.method == "PUT"
        assert request.read()
        assert request.url.path == "/payment/api/v1/merchant-integration/discounts"
        return httpx.Response(
            200,
            json={
                "updateResult": [
                    {
                        "success": False,
                        "error": {"discountId": "discount-1", "errorMessage": "already ended"},
                    }
                ]
            },
        )

    result = resource_for(handler).update_discounts_in_bulk(
        UpdateDiscountsRequest(
            discounts=[
                UpdateDiscount(
                    discount_id="discount-1",
                    new_date_from="22/07/2022",
                    new_discount_price="900",
                    new_discount_type=DiscountType.CLEARANCE_SALE,
                )
            ]
        )
    )
    assert result.update_result[0].error.error_message == "already ended"


def test_get_discount_prices_formats_dates_and_parses_datetimes():
    def handler(request):
        assert request.method == "GET"
        assert dict(request.url.params) == {
            "dateFrom": "01/08/2026",
            "dateTo": "20/08/2026",
        }
        return httpx.Response(
            200,
            json=[
                {
                    "discountId": "discount-1",
                    "merchantInventoryId": 889,
                    "discountPrice": 2000,
                    "dateFrom": "2022-01-26T00:00:00",
                    "dateTo": "2022-01-28T00:00:00",
                }
            ],
        )

    prices = resource_for(handler).get_discount_prices(
        date_from=date(2026, 8, 1), date_to="20/08/2026"
    )
    assert prices[0].merchant_inventory_id == 889
    assert prices[0].date_from == datetime(2022, 1, 26)


def test_cancel_discount_prices_escapes_id_and_returns_message():
    def handler(request):
        assert request.method == "PUT"
        assert request.url.raw_path.endswith(b"/discount%2F1/cancellations")
        return httpx.Response(200, json={"message": "Success"})

    result = resource_for(handler).cancel_discount_prices("discount/1")
    assert result.message == "Success"


@pytest.mark.parametrize("value", ["2026-08-20", "31/02/2026", ""])
def test_request_dates_reject_invalid_formats(value):
    with pytest.raises(ValidationError):
        ScheduleDiscount(date_from=value)


def test_discount_type_rejects_unknown_value():
    with pytest.raises(ValidationError):
        ScheduleDiscount(discount_type="FLASH_SALE")


def test_query_dates_and_discount_id_are_validated_before_transport():
    resource = resource_for(lambda request: pytest.fail("transport should not be called"))
    with pytest.raises(ValueError, match="dd/MM/yyyy"):
        resource.get_discount_prices(date_from="31/02/2026", date_to="20/08/2026")
    with pytest.raises(ValueError, match="discount_id"):
        resource.cancel_discount_prices("  ")
