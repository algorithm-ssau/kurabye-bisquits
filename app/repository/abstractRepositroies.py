from abc import ABC, abstractmethod

from domain.entities.cart import Cart
from domain.entities.product import Product, ProductFullInfo
from schemas.user import UserResponseSchema


class AbstractUserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserResponseSchema):
        pass


class AbstractProductRepository(ABC):
    @abstractmethod
    async def get_product(self, product_id: int, package_id: int) -> ProductFullInfo | None:
        pass

    @abstractmethod
    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass


class AbstractCartRepository(ABC):
    @abstractmethod
    async def get_cart(self, cart_id: int) -> Cart | None:
        pass

    @abstractmethod
    async def add_product_to_cart(self, cart_id: int, product_id: int, product_quantity: int = 1) -> bool:
        pass

    @abstractmethod
    async def delete_product_from_cart(self, cart_id: int, product_id, product_quantity: None | int = None) -> bool:
        pass
