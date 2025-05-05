from uuid import UUID

from pydantic import BaseModel, Field

from domain.enums import ProductCalculus


class ProductResponseSchema(BaseModel):
    product_id: UUID
    name: str = Field(min_length=1, max_length=255)
    product_image: str
    price: float
    calculus: ProductCalculus = Field(default=ProductCalculus.IN_PACKAGES)
    quantity: int = Field(gt=0, default=1)


class ProductFullResponseSchema(ProductResponseSchema):
    description: str | None = Field(default=None, description="The information about the project.")
    composition: list = Field(description="The composition of the product, e.g.: milk, sugar and etc.")
    energy: int = Field(description="The energy of the product of the 100 grams, e.g. 100kCal")
    fats: int | None = Field(default=None)
    carbohydrates: int | None = Field(default=None)
    proteins: int | None = Field(default=None)


class ProductQueryParams(BaseModel):
    limit: int = Field(default=12, gt=0, le=25, description="Limit of the products on the page.")
    offset: int = Field(default=0, ge=0, description="Offset of the for products for the pagination.")
    sorting_by: str | None = Field(default=None, description="The rule of sorting the elements.")
    sorting_order: str = Field(
        pattern=r"^(asc|desc)$",
        default="asc",
        description="The sorting order, asc — from the least to the gretest, desc — from the greatest to the least.",
    )
