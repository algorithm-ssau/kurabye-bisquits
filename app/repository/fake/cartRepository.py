from collections import defaultdict
from uuid import UUID

from fastapi import Depends

from domain.entities.cart import Cart
from domain.entities.product import Product
from repository.abstractRepositroies import AbstractCartRepository
from repository.fake.productRepository import fake_products

cart_fake: dict[UUID, Cart | None] = defaultdict(lambda: None)
cart_fake[UUID("123e4567-e89b-12d3-a456-426614174000")] = Cart(
    cart_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    items=defaultdict(int),
)


class CartRepository(AbstractCartRepository):
    def __init__(self, session: None):
        self.__session = session

    async def add_product_to_cart(self, cart_id: UUID, product_id: UUID, product_quantity: int = 1) -> bool:
        if fake_products[product_id] and cart_fake[cart_id]:
            product_to_cart = Product(**fake_products[product_id].model_dump())
            cart_fake[cart_id].items[product_to_cart] += product_quantity
            return True
        return False

    async def delete_product_from_cart(self, cart_id: UUID, product_id, product_quantity: None | int = None) -> bool:
        if fake_products[product_id] and cart_fake[cart_id]:
            product_to_delete = Product(**fake_products[product_id].model_dump())

            if cart_fake[cart_id]:
                if not product_quantity:
                    del cart_fake[cart_id].items[product_to_delete]
                    return True
                product_remains = cart_fake[cart_id].items[product_to_delete] - product_quantity
                if product_remains > 0:
                    cart_fake[cart_id].items[product_to_delete] -= product_quantity
                else:
                    del cart_fake[cart_id].items[product_to_delete]
                return True

        return False

    async def get_cart(self, cart_id: UUID) -> Cart | None:
        return cart_fake[cart_id] if cart_fake[cart_id] else None


get_session = lambda: None  # noqa: E731


def get_cart_repository(session=Depends(get_session)) -> AbstractCartRepository:
    return CartRepository(session=session)
