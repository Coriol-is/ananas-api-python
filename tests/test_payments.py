from __future__ import annotations

from typing import Any

import httpx
import pytest

from ananas_api.client import AnanasClient
from ananas_api.models.payments import InvoiceType
from ananas_api.resources.payments import PaymentsResource


def resource(response: Any, requests: list[httpx.Request]) -> PaymentsResource:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=response)

    http = httpx.Client(base_url="https://api.example.test", transport=httpx.MockTransport(handler))
    client = AnanasClient(
        base_url="https://api.example.test", access_token="token", http_client=http
    )
    return PaymentsResource(client)


def test_get_merchant_warehouses() -> None:
    requests: list[httpx.Request] = []
    result = resource(
        {"content": [{"id": 2, "warehouseName": "Airport", "defaultAddress": True}]},
        requests,
    ).get_merchant_warehouses()

    assert result.content is not None
    assert result.content[0].warehouse_name == "Airport"
    assert requests[0].url.path == "/order/api/v1/merchant-integration/merchant-warehouses"


FULL_INVOICE = {
    "invoiceHeader": {
        "invoiceType": "FISCAL",
        "merchantDetails": {
            "name": "Merchant",
            "businessSpaceCode": "B1",
            "taxIdentificationNumber": "111",
            "identificationNumber": "222",
            "taxAdministrationId": "TA",
            "cashier": "Cashier",
            "contactDetails": {"phone": "+381", "email": "m@example.test"},
            "address": {"street": "Main 1", "city": "Belgrade"},
        },
        "customerDetails": {
            "firstName": "Pera",
            "lastName": "Peric",
            "address": {"street": "Side 2", "city": "Novi Sad", "postcode": "21000"},
        },
        "fiscalDetails": {
            "invoiceCounter": "1/1",
            "verificationUrl": "https://verify.example.test",
            "fiscalInvoiceDate": "2022-05-03T18:51:18Z",
            "invoiceNumber": "INV-1",
        },
        "orderDetails": {
            "invoiceId": "4599",
            "invoicedDate": "2022-05-03T00:00:00Z",
            "orderid": "ORDER-1",
            "suborderId": "ORDER-1-1",
            "fba": False,
            "paymentMethods": ["PBC"],
            "warehouseAddress": {"warehouseId": 2, "street": "Main 1", "city": "Belgrade"},
            "orderDate": "2022-05-02T00:00:00Z",
        },
    },
    "productSpecification": {
        "items": [
            {
                "productDetails": {
                    "name": "TV",
                    "apId": "AP1",
                    "sku": "SKU1",
                    "ean": "8601",
                    "acode": "A1",
                },
                "quantity": 1,
                "itemPrice": {
                    "unitPrice": 120,
                    "unitPriceWithoutVat": 100,
                    "basePrice": 110,
                    "basePriceWithoutVat": 91.67,
                    "discountVat": 8.33,
                    "discountAmount": 10,
                    "vat": 20,
                    "vatAmount": 18.33,
                },
                "grandTotalPrice": {
                    "unitPrice": 120,
                    "unitPriceWithoutVat": 100,
                    "basePrice": 110,
                    "basePriceWithoutVat": 91.67,
                    "discountVat": 8.33,
                    "discountAmount": 10,
                    "vat": 20,
                    "vatAmount": 18.33,
                },
            }
        ],
        "totalDetails": {
            "basePrice": 110,
            "basePriceWithoutVat": 91.67,
            "vatAmount": 18.33,
            "chargedPrice": 110,
        },
    },
    "taxRateSpecification": {
        "taxRateSpecification": [
            {
                "label": "A",
                "name": "VAT",
                "basePriceWithoutVat": 91.67,
                "vat": 20,
                "vatAmount": 18.33,
            }
        ],
        "grandTotal": 18.33,
    },
}


def test_get_all_invoices_parses_full_nested_schema_and_query() -> None:
    requests: list[httpx.Request] = []
    result = resource([FULL_INVOICE], requests).get_all_invoices(
        date_from="2022-05-01T00:00:00Z",
        date_to="2022-05-31T00:00:00Z",
        invoice_type=InvoiceType.FISCAL,
    )

    invoice = result.root[0]
    assert invoice.invoice_header.customer_details.address.postcode == "21000"  # type: ignore[union-attr]
    assert invoice.product_specification.items[0].item_price.vat_amount == 18.33  # type: ignore[union-attr]
    assert invoice.tax_rate_specification.tax_rate_specification[0].name == "VAT"  # type: ignore[union-attr]
    assert requests[0].url.params["type"] == "FISCAL"
    assert requests[0].url.path == "/order/api/v1/merchant-integration/invoices"


def test_get_invoice_corrections_models_correction_only_fields() -> None:
    requests: list[httpx.Request] = []
    correction = {**FULL_INVOICE, "invoiceHeader": {**FULL_INVOICE["invoiceHeader"]}}
    correction["invoiceHeader"]["invoiceCorrectionReason"] = "Return"
    correction["invoiceHeader"]["fiscalDetails"] = {
        "invoiceCounter": "1/2",
        "referentDocumentNumber": "INV-1",
    }
    correction["invoiceHeader"]["orderDetails"] = {
        "invoiceNumber": "COR-1",
        "fba": "false",
    }
    result = resource([correction], requests).get_all_invoice_corrections(
        date_from="2022-05-01", date_to="2022-05-31", invoice_type="NON_FISCAL"
    )

    header = result.root[0].invoice_header
    assert header is not None
    assert header.invoice_correction_reason == "Return"
    assert header.fiscal_details.referent_document_number == "INV-1"  # type: ignore[union-attr]
    assert requests[0].url.path.endswith("/invoice-corrections")


def test_get_merchant_inventory_prices_joins_ids() -> None:
    requests: list[httpx.Request] = []
    result = resource(
        [
            {
                "merchantInventoryId": 1776331,
                "basePrice": 24000,
                "sellablePrice": 18000,
                "discountId": "d1",
            }
        ],
        requests,
    ).get_merchant_inventory_prices(date_from="2026-08-20", merchant_inventory_ids=[1, 2])

    assert result.root[0].merchant_inventory_id == 1776331
    assert requests[0].url.params["merchantInventoryIds"] == "1,2"
    assert requests[0].url.path == "/payment/api/v1/merchant-integration/prices"


@pytest.mark.parametrize(
    ("method", "suffix"),
    [
        ("get_invoice_urls", "/invoices/urls"),
        ("get_invoice_corrections_urls", "/invoice-corrections/urls"),
    ],
)
def test_get_invoice_document_urls(method: str, suffix: str) -> None:
    requests: list[httpx.Request] = []
    payments = resource(
        {
            "suborderIdNumberValue": [
                {"documentCorrelationId": "doc-1", "link": "https://example.test/a.pdf"}
            ]
        },
        requests,
    )
    result = getattr(payments, method)(
        date_from="2022-05-01", date_to="2022-05-31", suborder_ids=["SUB-1", "SUB-2"]
    )

    assert result.suborder_id_number_value[0].document_correlation_id == "doc-1"  # type: ignore[index,union-attr]
    assert requests[0].url.path.endswith(suffix)
    assert requests[0].url.params["suborderIds"] == "SUB-1,SUB-2"


def test_payment_parameter_validation_happens_before_request() -> None:
    payments = resource([], [])
    with pytest.raises(ValueError, match="date_from must not be after"):
        payments.get_all_invoices(date_from="2022-06-01", date_to="2022-05-01")
    with pytest.raises(ValueError, match="FISCAL or NON_FISCAL"):
        payments.get_all_invoices(
            date_from="2022-05-01", date_to="2022-06-01", invoice_type="OTHER"
        )
    with pytest.raises(ValueError, match="more than 100"):
        payments.get_merchant_inventory_prices(
            date_from="2026-08-20", merchant_inventory_ids=list(range(101))
        )
    with pytest.raises(ValueError, match="at least one"):
        payments.get_invoice_urls(date_from="2022-05-01", date_to="2022-06-01", suborder_ids=[])
