"""Typed models for the Ananas Products API."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


class ProductModel(BaseModel):
    """Base model preserving the JSON field names used by Ananas."""

    model_config = ConfigDict(populate_by_name=True)


class PackageWeightUnit(str, Enum):
    KG = "KG"
    G = "G"


class Warehouse(str, Enum):
    ANANAS_WAREHOUSE = "ANANAS_WAREHOUSE"
    MERCHANT_WAREHOUSE = "MERCHANT_WAREHOUSE"


class ProductRequest(ProductModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    ean: Optional[str] = None
    brand: Optional[str] = None
    gallery: Optional[List[str]] = None
    parent_ean: Optional[str] = Field(None, alias="parentEan")
    package_weight_value: Optional[float] = Field(None, alias="packageWeightValue", ge=0)
    package_weight_unit: PackageWeightUnit = Field(PackageWeightUnit.KG, alias="packageWeightUnit")
    base_price: Optional[float] = Field(None, alias="basePrice", ge=0)
    vat: Optional[float] = Field(None, ge=0)
    stock_level: Optional[int] = Field(None, alias="stockLevel", ge=0)
    sku: Optional[str] = None
    external_id: Optional[str] = Field(None, alias="externalId")
    product_type: Optional[str] = Field(None, alias="productType")
    category: Optional[str] = None
    attributes: Optional[Dict[str, List[str]]] = None


# Name from the OpenAPI document retained as an import-friendly alias.
ProductsRequest = ProductRequest


class UpdateProductRequest(ProductModel):
    id: Optional[int] = Field(None, gt=0)
    package_weight_value: Optional[float] = Field(None, alias="packageWeightValue", ge=0)
    package_weight_unit: PackageWeightUnit = Field(PackageWeightUnit.KG, alias="packageWeightUnit")
    base_price: Optional[float] = Field(None, alias="basePrice", ge=0)
    vat: Optional[float] = Field(None, ge=0)
    stock_level: Optional[int] = Field(None, alias="stockLevel", ge=0)
    sku: Optional[str] = None


class UpdateProductsRequest(RootModel[List[UpdateProductRequest]]):
    pass


class CheckIfEANExistsRequest(RootModel[List[str]]):
    @field_validator("root")
    @classmethod
    def validate_eans(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("at least one EAN is required")
        if any(not ean.strip() for ean in value):
            raise ValueError("EAN values must not be empty")
        return value


class ProductResponse(ProductModel):
    id: Optional[int] = None
    external_id: Optional[str] = Field(None, alias="externalId")
    ean: Optional[str] = None
    ananas_code: Optional[str] = Field(None, alias="ananasCode")
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    product_type: Optional[str] = Field(None, alias="productType")
    categories: Optional[List[str]] = None
    new_base_price: Optional[float] = Field(None, alias="newBasePrice")
    base_price: Optional[float] = Field(None, alias="basePrice")
    vat: Optional[float] = None
    stock_level: Optional[float] = Field(None, alias="stockLevel")
    package_weight_value: Optional[float] = Field(None, alias="packageWeightValue")
    package_weight_unit: Optional[str] = Field(None, alias="packageWeightUnit")


ProductsResponse = ProductResponse


class BasicProductResponse(ProductModel):
    id: Optional[int] = None
    ean: Optional[str] = None
    sku: Optional[str] = None
    new_base_price: Optional[float] = Field(None, alias="newBasePrice")
    base_price: Optional[float] = Field(None, alias="basePrice")
    stock_level: Optional[float] = Field(None, alias="stockLevel")
    warehouse: Optional[Warehouse] = None


ProductsBasicResponse = BasicProductResponse


class ImportProductsResponse(ProductModel):
    id: Optional[str] = None


class ProductUpdateResult(ProductModel):
    status: Optional[str] = None
    errors: Optional[List[Any]] = None
    my_product_id: Optional[float] = Field(None, alias="myProductId")


UpdateSingleProductResponse = ProductUpdateResult


class UpdateProductsResponse(RootModel[List[ProductUpdateResult]]):
    pass


class ProductTypesResponse(RootModel[List[str]]):
    pass


class CheckIfEANExistsResponse(RootModel[Dict[str, bool]]):
    pass
