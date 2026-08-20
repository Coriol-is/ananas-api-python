"""Models returned by the warehouse, invoice, and payment endpoints."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from pydantic import Field, RootModel

from .base import APIResponseModel


class InvoiceType(str, Enum):
    FISCAL = "FISCAL"
    NON_FISCAL = "NON_FISCAL"


class MerchantWarehouse(APIResponseModel):
    id: Optional[float] = None
    warehouse_name: Optional[str] = Field(None, alias="warehouseName")
    default_address: Optional[bool] = Field(None, alias="defaultAddress")


class MerchantWarehousesResponse(APIResponseModel):
    content: Optional[List[MerchantWarehouse]] = None


class ContactDetails(APIResponseModel):
    phone: Optional[str] = None
    email: Optional[str] = None


class MerchantAddress(APIResponseModel):
    street: Optional[str] = None
    city: Optional[str] = None


class CustomerAddress(MerchantAddress):
    postcode: Optional[str] = None


class MerchantDetails(APIResponseModel):
    name: Optional[str] = None
    business_space_code: Optional[str] = Field(None, alias="businessSpaceCode")
    tax_identification_number: Optional[str] = Field(None, alias="taxIdentificationNumber")
    identification_number: Optional[str] = Field(None, alias="identificationNumber")
    tax_administration_id: Optional[str] = Field(None, alias="taxAdministrationId")
    cashier: Optional[str] = None
    contact_details: Optional[ContactDetails] = Field(None, alias="contactDetails")
    address: Optional[MerchantAddress] = None


class CustomerDetails(APIResponseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    address: Optional[CustomerAddress] = None


class FiscalDetails(APIResponseModel):
    invoice_counter: Optional[str] = Field(None, alias="invoiceCounter")
    verification_url: Optional[str] = Field(None, alias="verificationUrl")
    fiscal_invoice_date: Optional[str] = Field(None, alias="fiscalInvoiceDate")
    invoice_number: Optional[str] = Field(None, alias="invoiceNumber")
    referent_document_number: Optional[str] = Field(None, alias="referentDocumentNumber")


class WarehouseAddress(APIResponseModel):
    warehouse_id: Optional[int] = Field(None, alias="warehouseId")
    street: Optional[str] = None
    city: Optional[str] = None


class OrderDetails(APIResponseModel):
    invoice_id: Optional[str] = Field(None, alias="invoiceId")
    invoice_number: Optional[str] = Field(None, alias="invoiceNumber")
    invoiced_date: Optional[str] = Field(None, alias="invoicedDate")
    order_id: Optional[str] = Field(None, alias="orderid")
    suborder_id: Optional[str] = Field(None, alias="suborderId")
    # The invoices schema declares boolean; corrections declares string.
    fba: Optional[Union[bool, str]] = None
    payment_methods: Optional[List[str]] = Field(None, alias="paymentMethods")
    warehouse_address: Optional[WarehouseAddress] = Field(None, alias="warehouseAddress")
    order_date: Optional[str] = Field(None, alias="orderDate")


class InvoiceHeader(APIResponseModel):
    invoice_type: Optional[InvoiceType] = Field(None, alias="invoiceType")
    invoice_correction_reason: Optional[str] = Field(None, alias="invoiceCorrectionReason")
    merchant_details: Optional[MerchantDetails] = Field(None, alias="merchantDetails")
    customer_details: Optional[CustomerDetails] = Field(None, alias="customerDetails")
    fiscal_details: Optional[FiscalDetails] = Field(None, alias="fiscalDetails")
    order_details: Optional[OrderDetails] = Field(None, alias="orderDetails")


class ProductDetails(APIResponseModel):
    name: Optional[str] = None
    ap_id: Optional[str] = Field(None, alias="apId")
    sku: Optional[str] = None
    ean: Optional[str] = None
    acode: Optional[str] = None


class PriceDetails(APIResponseModel):
    unit_price: Optional[float] = Field(None, alias="unitPrice")
    unit_price_without_vat: Optional[float] = Field(None, alias="unitPriceWithoutVat")
    base_price: Optional[float] = Field(None, alias="basePrice")
    base_price_without_vat: Optional[float] = Field(None, alias="basePriceWithoutVat")
    discount_vat: Optional[float] = Field(None, alias="discountVat")
    discount_amount: Optional[float] = Field(None, alias="discountAmount")
    vat: Optional[float] = None
    vat_amount: Optional[float] = Field(None, alias="vatAmount")


class InvoiceItem(APIResponseModel):
    product_details: Optional[ProductDetails] = Field(None, alias="productDetails")
    quantity: Optional[int] = None
    item_price: Optional[PriceDetails] = Field(None, alias="itemPrice")
    grand_total_price: Optional[PriceDetails] = Field(None, alias="grandTotalPrice")


class TotalDetails(APIResponseModel):
    base_price: Optional[float] = Field(None, alias="basePrice")
    base_price_without_vat: Optional[float] = Field(None, alias="basePriceWithoutVat")
    vat_amount: Optional[float] = Field(None, alias="vatAmount")
    charged_price: Optional[float] = Field(None, alias="chargedPrice")


class ProductSpecification(APIResponseModel):
    items: Optional[List[InvoiceItem]] = None
    total_details: Optional[TotalDetails] = Field(None, alias="totalDetails")


class TaxRate(APIResponseModel):
    label: Optional[str] = None
    name: Optional[str] = None
    base_price_without_vat: Optional[float] = Field(None, alias="basePriceWithoutVat")
    vat: Optional[float] = None
    vat_amount: Optional[float] = Field(None, alias="vatAmount")


class TaxRateSpecification(APIResponseModel):
    tax_rate_specification: Optional[List[TaxRate]] = Field(None, alias="taxRateSpecification")
    grand_total: Optional[float] = Field(None, alias="grandTotal")


class Invoice(APIResponseModel):
    invoice_header: Optional[InvoiceHeader] = Field(None, alias="invoiceHeader")
    product_specification: Optional[ProductSpecification] = Field(
        None, alias="productSpecification"
    )
    tax_rate_specification: Optional[TaxRateSpecification] = Field(
        None, alias="taxRateSpecification"
    )


class InvoicesResponse(RootModel[List[Invoice]]):
    pass


class InvoiceCorrection(Invoice):
    pass


class InvoiceCorrectionsResponse(RootModel[List[InvoiceCorrection]]):
    pass


class MerchantInventoryPrice(APIResponseModel):
    merchant_inventory_id: Optional[float] = Field(None, alias="merchantInventoryId")
    base_price: Optional[float] = Field(None, alias="basePrice")
    sellable_price: Optional[float] = Field(None, alias="sellablePrice")
    discount_id: Optional[str] = Field(None, alias="discountId")


class PricesDataResponse(RootModel[List[MerchantInventoryPrice]]):
    pass


class InvoiceDocumentURL(APIResponseModel):
    document_correlation_id: Optional[str] = Field(None, alias="documentCorrelationId")
    link: Optional[str] = None


class InvoiceURLsResponse(APIResponseModel):
    suborder_id_number_value: Optional[List[InvoiceDocumentURL]] = Field(
        None, alias="suborderIdNumberValue"
    )
