from abc import ABC, abstractmethod

from domain.entities.cart import Cart
from domain.entities.product import Product, ProductFullInfo
from domain.entities.user import CreateUser, User, UserWithCreds


class AbstractProductService(ABC):
    @abstractmethod
    async def get_product(self, product_id: int) -> ProductFullInfo | None:
        pass

    @abstractmethod
    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass


class AbstractCartService(ABC):
    @abstractmethod
    async def get_cart(self, cart_id: int) -> Cart | None:
        pass

    @abstractmethod
    async def create_cart(self, cart_id: int) -> bool: ...

    @abstractmethod
    async def add_product_to_cart(self, cart_id: int, product_id: int, product_quantity: int = 1) -> bool:
        pass

    @abstractmethod
    async def delete_product_from_cart(self, cart_id: int, product_id, product_quantity: None | int = None) -> bool:
        pass


class AbstractUserService(ABC):
    @abstractmethod
    async def get_user(self, user_login: str) -> User | None: ...

    @abstractmethod
    async def get_user_creds(self, user_login: str) -> UserWithCreds | None: ...

    @abstractmethod
    async def add_user(self, user_data: CreateUser) -> User | None: ...
