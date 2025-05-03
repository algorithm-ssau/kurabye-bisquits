from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.product import Product


class CartItem(BaseModel):
    product: Product
    product_quantity: int = Field(gt=0, default=1)


class Cart(BaseModel):
    user_id: UUID
    cart_id: UUID
    items: list[CartItem] = []
