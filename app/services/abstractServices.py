from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.cart import Cart
from domain.entities.product import Product


class AbstractProductService(ABC):
    @abstractmethod
    async def get_product(self, product_id: UUID) -> Product | None:
        pass

    @abstractmethod
    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass


class AbstractCartService(ABC):
    @abstractmethod
    async def get_cart(self, card_id: UUID) -> Cart | None:
        pass

    @abstractmethod
    async def add_product_to_cart(self, cart_id: UUID, product_id: UUID, quantity: int = 1) -> bool:
        pass

    @abstractmethod
    async def delete_product_from_cart(self, cart_id: UUID, product_id, quantity: None | int = None) -> bool:
        pass
