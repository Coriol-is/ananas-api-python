from ananas_api import AnanasClient
from ananas_api.models import OPENAPI_SCHEMA_MODELS


def test_all_openapi_component_schemas_have_typed_models() -> None:
    assert set(OPENAPI_SCHEMA_MODELS) == {
        "CheckIfEANExistsRequest",
        "CheckIfEANExistsResponse",
        "GetDiscountPricesResponse",
        "ImportProductsResponse",
        "InvoiceCorrectionsResponse",
        "InvoiceURLsResponse",
        "InvoicesResponse",
        "MerchantWarehousesResponse",
        "PricesDataResponse",
        "ProductTypesResponse",
        "ProductsBasicResponse",
        "ProductsRequest",
        "ProductsResponse",
        "ScheduleDiscountsRequest",
        "ScheduleDiscountsResponse",
        "Token",
        "TokenResponse",
        "UpdateDiscountsRequest",
        "UpdateDiscountsResponse",
        "UpdateProductRequest",
        "UpdateProductsRequest",
        "UpdateProductsResponse",
        "UpdateSingleProductResponse",
    }


def test_all_openapi_operations_have_named_methods() -> None:
    client = AnanasClient(base_url="https://api.example.test", access_token="token")
    operations = {
        "token": client.authenticate,
        "getProducts": client.products.get_products,
        "getBasicProducts": client.products.get_basic_products,
        "importOrUpdateProducts": client.products.import_or_update_products,
        "updateProducts": client.products.update_products,
        "updateSingleProduct": client.products.update_single_product,
        "getProductsTypes": client.products.get_products_types,
        "checkIfEANExists": client.products.check_if_ean_exists,
        "getMerchantWarehouses": client.payments.get_merchant_warehouses,
        "GetAllInvoices": client.payments.get_all_invoices,
        "GetAllInvoiceCorrections": client.payments.get_all_invoice_corrections,
        "scheduleDiscountsInBulk": client.discounts.schedule_discounts_in_bulk,
        "updateDiscountsInBulk": client.discounts.update_discounts_in_bulk,
        "getDiscountPrices": client.discounts.get_discount_prices,
        "cancelDiscountPrices": client.discounts.cancel_discount_prices,
        "GetMerchantInventoryPrices": client.payments.get_merchant_inventory_prices,
        "GetInvoiceURLs": client.payments.get_invoice_urls,
        "GetInvoiceCorrectionsURLs": client.payments.get_invoice_corrections_urls,
    }

    assert len(operations) == 18
    assert all(callable(operation) for operation in operations.values())
    assert client.warehouses is client.payments
    client.close()
