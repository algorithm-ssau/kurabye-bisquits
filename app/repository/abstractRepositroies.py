from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.user import UserResponseSchema
from domain.entities.product import Product


class AbstractUserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserResponseSchema):
        pass


class AbstractProductRepository(ABC):
    @abstractmethod
    async def get_product(self, product_id: UUID) -> Product | None:
        pass

    @abstractmethod
    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass
