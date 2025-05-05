from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException

from schemas.cart import AddProductToCartRequest, DeleteProductFromCartRequest
from services.cartService import get_cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/{product_id}")
async def add_product_to_cart(
    product_to_cart: AddProductToCartRequest = Body(),
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


@router.get("/")
async def get_cart(cart_id: UUID, cart_service=Depends(get_cart_service)):
    cart = await cart_service.get_cart(cart_id=cart_id)
    if cart:
        return cart
    raise HTTPException(status_code=404, detail="Cart doesn't exists.")


@router.delete("/{product_id}")
async def delete_product_from_cart(
    product_delete: DeleteProductFromCartRequest = Body(),
    cart_service=Depends(get_cart_service),
):
    is_product_deleted = await cart_service.delete_product_from_cart(
        cart_id=product_delete.cart_id,
        product_id=product_delete.product_id,
        product_quantity=product_delete.product_quantity,
    )
    if is_product_deleted:
        return {"status": "success"}

    raise HTTPException(status_code=404)
