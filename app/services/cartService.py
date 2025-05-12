from fastapi import Depends

from domain.entities.cart import Cart
from repository.abstractRepositroies import AbstractCartRepository
from repository.cartRepository import get_cart_repository
from services.abstractServices import AbstractCartService


class CartService(AbstractCartService):
    def __init__(self, cart_repository):
        self.__cart_repository: AbstractCartRepository = cart_repository

    async def get_cart(self, cart_id: int) -> Cart | None:
        return await self.__cart_repository.get_cart(cart_id=cart_id)

    async def create_cart(self, cart_id: int) -> bool:
        return await self.__cart_repository.create_cart(cart_id)

    async def add_product_to_cart(self, cart_id: int, product_id: int, product_quantity: int = 1) -> bool:
        # TODO: check that product exists and quantity of product in the warehouse > 0
        return await self.__cart_repository.add_product_to_cart(
            cart_id=cart_id,
            product_id=product_id,
            product_quantity=product_quantity,
        )

    async def delete_product_from_cart(self, cart_id: int, product_id, product_quantity: None | int = None) -> bool:
        # if product_quantity is None, than will deleted all products from the cart
        return await self.__cart_repository.delete_product_from_cart(
            cart_id=cart_id,
            product_id=product_id,
            product_quantity=product_quantity,
        )


def get_cart_service(cart_repository=Depends(get_cart_repository)):
    return CartService(cart_repository=cart_repository)
