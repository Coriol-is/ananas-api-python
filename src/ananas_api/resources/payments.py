"""Warehouse, invoice, and payment endpoint methods."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Sequence, Union

from ..models.payments import (
    InvoiceCorrectionsResponse,
    InvoicesResponse,
    InvoiceType,
    InvoiceURLsResponse,
    MerchantWarehousesResponse,
    PricesDataResponse,
)
from .base import Resource

DateValue = Union[str, date, datetime]


def _date_param(value: DateValue, name: str) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty ISO-8601 date or datetime")
    candidate = value.strip()
    try:
        datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 date or datetime") from exc
    return candidate


def _date_range(date_from: DateValue, date_to: DateValue) -> tuple[str, str]:
    start = _date_param(date_from, "date_from")
    end = _date_param(date_to, "date_to")
    try:
        start_value = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_value = datetime.fromisoformat(end.replace("Z", "+00:00"))
        if start_value > end_value:
            raise ValueError("date_from must not be after date_to")
    except TypeError:
        # Comparing an offset-aware value with a naive one is ambiguous.
        raise ValueError("date_from and date_to must use compatible timezone information") from None
    return start, end


def _invoice_type(value: Optional[Union[InvoiceType, str]]) -> Optional[str]:
    if value is None:
        return None
    try:
        return InvoiceType(value).value
    except ValueError as exc:
        raise ValueError("invoice_type must be FISCAL or NON_FISCAL") from exc


def _joined(values: Union[str, Sequence[Union[str, int]]], name: str, limit: int = 0) -> str:
    if isinstance(values, str):
        items = [item.strip() for item in values.split(",")]
    else:
        items = [str(item).strip() for item in values]
    if not items or any(not item for item in items):
        raise ValueError(f"{name} must contain at least one non-empty value")
    if limit and len(items) > limit:
        raise ValueError(f"{name} cannot contain more than {limit} values")
    return ",".join(items)


class PaymentsResource(Resource):
    """Named methods for the Ananas warehouse and payment APIs."""

    def get_merchant_warehouses(self) -> MerchantWarehousesResponse:
        payload = self._client.request(
            "GET", "/order/api/v1/merchant-integration/merchant-warehouses"
        )
        return MerchantWarehousesResponse.model_validate(payload)

    def get_all_invoices(
        self,
        *,
        date_from: DateValue,
        date_to: DateValue,
        invoice_type: Optional[Union[InvoiceType, str]] = None,
    ) -> InvoicesResponse:
        params = self._invoice_params(date_from, date_to, invoice_type)
        payload = self._client.request(
            "GET", "/order/api/v1/merchant-integration/invoices", params=params
        )
        return InvoicesResponse.model_validate(payload)

    def get_all_invoice_corrections(
        self,
        *,
        date_from: DateValue,
        date_to: DateValue,
        invoice_type: Optional[Union[InvoiceType, str]] = None,
    ) -> InvoiceCorrectionsResponse:
        params = self._invoice_params(date_from, date_to, invoice_type)
        payload = self._client.request(
            "GET", "/order/api/v1/merchant-integration/invoice-corrections", params=params
        )
        return InvoiceCorrectionsResponse.model_validate(payload)

    def get_merchant_inventory_prices(
        self,
        *,
        date_from: DateValue,
        merchant_inventory_ids: Union[str, Sequence[Union[str, int]]],
    ) -> PricesDataResponse:
        params = {
            "dateFrom": _date_param(date_from, "date_from"),
            "merchantInventoryIds": _joined(
                merchant_inventory_ids, "merchant_inventory_ids", limit=100
            ),
        }
        payload = self._client.request(
            "GET", "/payment/api/v1/merchant-integration/prices", params=params
        )
        return PricesDataResponse.model_validate(payload)

    def get_invoice_urls(
        self,
        *,
        date_from: DateValue,
        date_to: DateValue,
        suborder_ids: Union[str, Sequence[str]],
        invoice_type: Optional[Union[InvoiceType, str]] = None,
    ) -> InvoiceURLsResponse:
        return self._get_invoice_urls(
            "/order/api/v1/merchant-integration/invoices/urls",
            date_from,
            date_to,
            suborder_ids,
            invoice_type,
        )

    def get_invoice_corrections_urls(
        self,
        *,
        date_from: DateValue,
        date_to: DateValue,
        suborder_ids: Union[str, Sequence[str]],
        invoice_type: Optional[Union[InvoiceType, str]] = None,
    ) -> InvoiceURLsResponse:
        return self._get_invoice_urls(
            "/order/api/v1/merchant-integration/invoice-corrections/urls",
            date_from,
            date_to,
            suborder_ids,
            invoice_type,
        )

    @staticmethod
    def _invoice_params(
        date_from: DateValue,
        date_to: DateValue,
        invoice_type: Optional[Union[InvoiceType, str]],
    ) -> dict[str, str]:
        start, end = _date_range(date_from, date_to)
        params = {"dateFrom": start, "dateTo": end}
        kind = _invoice_type(invoice_type)
        if kind is not None:
            params["type"] = kind
        return params

    def _get_invoice_urls(
        self,
        path: str,
        date_from: DateValue,
        date_to: DateValue,
        suborder_ids: Union[str, Sequence[str]],
        invoice_type: Optional[Union[InvoiceType, str]],
    ) -> InvoiceURLsResponse:
        params = self._invoice_params(date_from, date_to, invoice_type)
        params["suborderIds"] = _joined(suborder_ids, "suborder_ids")
        payload = self._client.request("GET", path, params=params)
        return InvoiceURLsResponse.model_validate(payload)
