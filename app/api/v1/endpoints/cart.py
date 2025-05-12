from fastapi import APIRouter, Body, Depends, HTTPException

from core.config import log_setting
from domain.entities.order import CreateOrder
from domain.exceptions.productExceptions import InsufficientStockError
from repository.abstractRepositroies import AbstractOrderRepository
from repository.orderRepository import get_order_repository
from schemas.cart import AddProductToCartRequest, CartResponseSchema, DeleteProductFromCartRequest
from schemas.order import CreateOrderSchema
from services.cartService import get_cart_service
from utils.cartUtils import get_cart_schema

router = APIRouter(prefix="/cart", tags=["Cart"])

log = log_setting.get_configure_logging(filename=__name__)


@router.patch("/{product_id}")
async def add_product_to_cart(
    product_to_cart: AddProductToCartRequest = Body(),
    cart_service=Depends(get_cart_service),
):
    try:
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
    except InsufficientStockError as error:
        raise HTTPException(status_code=402, detail="Нету такого количества продуктов на складе") from error


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


@router.post("/create_order")
async def create_order(
    order: CreateOrderSchema, order_service: AbstractOrderRepository = Depends(get_order_repository)
):
    await order_service.create_order(order=CreateOrder(**order.model_dump()))
    return {"status": "success"}


@router.get("/get_user_orders")
async def get_user_order(user_id: int, order_service: AbstractOrderRepository = Depends(get_order_repository)):
    return await order_service.get_user_orders(user_id=user_id)


@router.get("/get_order")
async def get_order(order_id: int, order_service: AbstractOrderRepository = Depends(get_order_repository)):
    return await order_service.get_order(order_id)
