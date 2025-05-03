from fastapi import APIRouter, Body, Depends, HTTPException

from schemas.cart import AddToCartRequest
from services.cartService import get_cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/{product_id}")
async def add_product_to_cart(
    product_to_cart: AddToCartRequest = Body(),
    cart_service=Depends(get_cart_service),
):
    status = await cart_service.add_product_to_cart(
        cart_id=product_to_cart.cart_id,
        product_id=product_to_cart.product_id,
        product_quantity=product_to_cart.product_quantity,
    )
    if status:
        return {"status": "success"}

    raise HTTPException(status_code=404)
