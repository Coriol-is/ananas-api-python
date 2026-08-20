"""Named methods for the Discounts API."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Union
from urllib.parse import quote

from ..models.discounts import (
    DiscountPrice,
    ScheduleDiscountsRequest,
    ScheduleDiscountsResponse,
    SuccessResponse,
    UpdateDiscountsRequest,
    UpdateDiscountsResponse,
)
from .base import Resource


class DiscountsResource(Resource):
    """Access discount scheduling, updates, queries, and cancellation."""

    PATH = "/payment/api/v1/merchant-integration/discounts"

    def schedule_discounts_in_bulk(
        self, request: ScheduleDiscountsRequest
    ) -> ScheduleDiscountsResponse:
        return self._request_model(
            ScheduleDiscountsResponse, "POST", self.PATH, json=request.to_payload()
        )

    def update_discounts_in_bulk(self, request: UpdateDiscountsRequest) -> UpdateDiscountsResponse:
        return self._request_model(
            UpdateDiscountsResponse, "PUT", self.PATH, json=request.to_payload()
        )

    def get_discount_prices(
        self, *, date_from: Union[date, str], date_to: Union[date, str]
    ) -> List[DiscountPrice]:
        params = {
            "dateFrom": self._format_query_date(date_from),
            "dateTo": self._format_query_date(date_to),
        }
        return self._request_as(List[DiscountPrice], "GET", self.PATH, params=params)

    def cancel_discount_prices(self, discount_id: str) -> SuccessResponse:
        if not isinstance(discount_id, str) or not discount_id.strip():
            raise ValueError("discount_id must not be empty")
        path = f"{self.PATH}/{quote(discount_id, safe='')}/cancellations"
        return self._request_model(SuccessResponse, "PUT", path)

    @staticmethod
    def _format_query_date(value: Union[date, str]) -> str:
        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%d/%m/%Y")
            except ValueError as exc:
                raise ValueError("date must use dd/MM/yyyy format") from exc
            return value
        raise TypeError("date must be a datetime.date or dd/MM/yyyy string")
