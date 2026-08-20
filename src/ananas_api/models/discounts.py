"""Models for the Discounts API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field, RootModel, field_validator

from .base import APIModel, APIResponseModel


class DiscountType(str, Enum):
    SALE = "SALE"
    SEASONAL_SALE = "SEASONAL_SALE"
    CLEARANCE_SALE = "CLEARANCE_SALE"


def _validate_api_date(value: Optional[str]) -> Optional[str]:
    if value is not None:
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError as exc:
            raise ValueError("date must use dd/MM/yyyy format") from exc
    return value


class ScheduleDiscount(APIModel):
    merchant_inventory_id: Optional[int] = Field(None, alias="merchantInventoryId")
    discount_price: Optional[float] = Field(None, alias="discountPrice")
    discount_price_currency: Optional[str] = Field(None, alias="discountPriceCurrency")
    date_from: Optional[str] = Field(None, alias="dateFrom")
    date_to: Optional[str] = Field(None, alias="dateTo")
    discount_type: Optional[DiscountType] = Field(None, alias="discountType")

    _date_from_format = field_validator("date_from")(_validate_api_date)
    _date_to_format = field_validator("date_to")(_validate_api_date)


class ScheduleDiscountsRequest(APIModel):
    discounts: Optional[List[ScheduleDiscount]] = None


class UpdateDiscount(APIModel):
    discount_id: Optional[str] = Field(None, alias="discountId")
    new_date_from: Optional[str] = Field(None, alias="newDateFrom")
    new_date_to: Optional[str] = Field(None, alias="newDateTo")
    new_discount_price: Optional[str] = Field(None, alias="newDiscountPrice")
    new_discount_price_currency: Optional[str] = Field(None, alias="newDiscountPriceCurrency")
    new_discount_type: Optional[DiscountType] = Field(None, alias="newDiscountType")

    _new_date_from_format = field_validator("new_date_from")(_validate_api_date)
    _new_date_to_format = field_validator("new_date_to")(_validate_api_date)


class UpdateDiscountsRequest(APIModel):
    discounts: Optional[List[UpdateDiscount]] = None


class ScheduledDiscountData(APIResponseModel):
    merchant_inventory_id: Optional[int] = Field(None, alias="merchantInventoryId")
    discount_id: Optional[str] = Field(None, alias="discountId")


class ScheduleDiscountError(APIResponseModel):
    merchant_inventory_id: Optional[int] = Field(None, alias="merchantInventoryId")
    error_message: Optional[str] = Field(None, alias="errorMessage")


class ScheduleDiscountResult(APIResponseModel):
    success: Optional[bool] = None
    data: Optional[ScheduledDiscountData] = None
    error: Optional[ScheduleDiscountError] = None


class ScheduleDiscountsResponse(APIResponseModel):
    schedule_result: Optional[List[ScheduleDiscountResult]] = Field(None, alias="scheduleResult")


class UpdatedDiscountData(APIResponseModel):
    discount_id: Optional[str] = Field(None, alias="discountId")


class UpdateDiscountError(APIResponseModel):
    discount_id: Optional[str] = Field(None, alias="discountId")
    error_message: Optional[str] = Field(None, alias="errorMessage")


class UpdateDiscountResult(APIResponseModel):
    success: Optional[bool] = None
    data: Optional[UpdatedDiscountData] = None
    error: Optional[UpdateDiscountError] = None


class UpdateDiscountsResponse(APIResponseModel):
    update_result: Optional[List[UpdateDiscountResult]] = Field(None, alias="updateResult")


class DiscountPrice(APIResponseModel):
    discount_id: Optional[str] = Field(None, alias="discountId")
    merchant_inventory_id: Optional[int] = Field(None, alias="merchantInventoryId")
    discount_price: Optional[float] = Field(None, alias="discountPrice")
    date_from: Optional[datetime] = Field(None, alias="dateFrom")
    date_to: Optional[datetime] = Field(None, alias="dateTo")


class GetDiscountPricesResponse(RootModel[List[DiscountPrice]]):
    pass


class SuccessResponse(APIResponseModel):
    message: Optional[str] = None
