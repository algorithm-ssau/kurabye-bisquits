from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.product import Product


class AbstractProductService(ABC):
    @abstractmethod
    async def get_product(self, product_id: UUID) -> Product | None:
        pass

    @abstractmethod
    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass
