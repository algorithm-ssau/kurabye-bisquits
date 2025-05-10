from fastapi import APIRouter, Body, Depends, HTTPException

from core.config import log_setting
from schemas.cart import AddProductToCartRequest, CartResponseSchema, DeleteProductFromCartRequest
from services.cartService import get_cart_service
from utils.cartUtils import get_cart_schema

router = APIRouter(prefix="/cart", tags=["Cart"])

log = log_setting.get_configure_logging(filename=__name__)


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
        log.info(
            "The product %s successfully added to cart %s in the %s quantity.",
            product_to_cart.product_id,
            product_to_cart.cart_id,
            product_to_cart.product_quantity,
        )
        return {"status": "success"}

    raise HTTPException(status_code=404)


@router.get("/", response_model=CartResponseSchema)
async def get_cart(cart_id: int, cart_service=Depends(get_cart_service)):
    cart = await cart_service.get_cart(cart_id=cart_id)

    if cart:
        return get_cart_schema(cart)
    raise HTTPException(status_code=404, detail="Cart doesn't exists.")


@router.delete("/{product_id}")
async def delete_product_from_cart(
    product_delete: DeleteProductFromCartRequest = Body(),
    cart_service=Depends(get_cart_service),
):
    # if product_quantity is None, than will deleted all products from the cart
    is_product_deleted = await cart_service.delete_product_from_cart(
        cart_id=product_delete.cart_id,
        product_id=product_delete.product_id,
        product_quantity=product_delete.product_quantity,
    )
    if is_product_deleted:
        log.info(
            "The %s %s product has deleted from the cart %s",
            product_delete.product_quantity,
            product_delete.product_id,
            product_delete.cart_id,
        )
        return {"status": "success"}

    raise HTTPException(status_code=404)
