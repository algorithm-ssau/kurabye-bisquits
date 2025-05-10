from abc import ABC, abstractmethod

from domain.entities.cart import Cart
from domain.entities.order import CreateOrder, Order, UpdateOrder
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

    @abstractmethod
    async def update_product(self, update_product: ProductFullInfo) -> ProductFullInfo | None:
        pass


class AbstractCartRepository(ABC):
    @abstractmethod
    async def create_cart(self, cart_id: int) -> bool:
        pass

    @abstractmethod
    async def get_cart(self, cart_id: int) -> Cart | None:
        pass

    @abstractmethod
    async def add_product_to_cart(self, cart_id: int, product_id: int, product_quantity: int = 1) -> bool:
        pass

    @abstractmethod
    async def delete_product_from_cart(self, cart_id: int, product_id, product_quantity: None | int = None) -> bool:
        pass


class AbstractOrderRepository(ABC):
    @abstractmethod
    async def create_order(self, order: CreateOrder) -> Order | None:
        pass

    @abstractmethod
    async def get_order(self, order_id: int) -> Order | None:
        pass

    @abstractmethod
    async def get_user_orders(
        self,
        user_id: int,
        status_id: int | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Order] | None:
        """
        If status_id is None, the method will return all users orders.
        """
        pass

    @abstractmethod
    async def set_order_items(self, cart_id: int, order_id: int) -> bool:
        pass

    @abstractmethod
    async def update_order(self, order_id, update_order: UpdateOrder) -> Order | None:
        pass

    @abstractmethod
    async def delete_order(self, order_id: int) -> bool:
        pass

    # TODO: in the future we want see the methods like add "new product into the order"
    #       and "delete products from the order"
