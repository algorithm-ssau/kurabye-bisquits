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
