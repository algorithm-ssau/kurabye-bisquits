from uuid import UUID

from domain.entities.product import Product
from services.abstractServices import AbstractProductService


class ProductService(AbstractProductService):
    def __init__(self, product_repository):
        self.__product_repository = product_repository

    async def get_product(self, product_id: UUID) -> Product | None:
        pass

    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass


def get_product_service(product_repository) -> ProductService:
    return ProductService(product_repository=product_repository)
