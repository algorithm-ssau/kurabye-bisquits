from uuid import UUID

from pydantic import BaseModel, Field


class AddProductToCartRequest(BaseModel):
    product_id: UUID
    cart_id: UUID
    product_quantity: int = Field(ge=0, default=1)


class DeleteProductFromCartRequest(BaseModel):
    product_id: UUID
    cart_id: UUID
    product_quantity: int = Field(ge=0, default=1)


class CartResponse(BaseModel):
    user_id: UUID
