from pydantic import BaseModel, Field

from domain.enums import ProductCalculus


class AddProductToCartRequest(BaseModel):
    product_id: int
    cart_id: int
    product_quantity: int = Field(default=1)


class DeleteProductFromCartRequest(BaseModel):
    product_id: int
    cart_id: int
    product_quantity: int | None = Field(ge=0, default=None)


class CartItemSchema(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    product_image: str
    price: float
    calculus: ProductCalculus = Field(default=ProductCalculus.IN_GRAMS)
    grammage: int | None = Field(gt=0, default=None)
    quantity: int = Field(ge=0, default=1)


class CartResponseSchema(BaseModel):
    cart_id: int
    items: dict[int, CartItemSchema]  # product_id : cart_product_scheme
