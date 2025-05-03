from uuid import UUID

from pydantic import BaseModel, Field


class AddToCartRequest(BaseModel):
    product_id: UUID
    cart_id: UUID
    product_quantity: int = Field(ge=0, default=1)
