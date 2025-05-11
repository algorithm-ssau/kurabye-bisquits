from fastapi import Depends

from domain.entities.product import Product, ProductFullInfo
from repository.abstractRepositroies import AbstractProductRepository
from repository.productRepository import get_product_repository
from services.abstractServices import AbstractProductService


class ProductService(AbstractProductService):
    def __init__(self, product_repository):
        self.__product_repository: AbstractProductRepository = product_repository

    async def get_product(self, product_id: int) -> ProductFullInfo | None:
        return await self.__product_repository.get_product(product_id)

    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        return await self.__product_repository.get_products(limit=limit, offset=offset)


def get_product_service(product_repository=Depends(get_product_repository)) -> AbstractProductService:
    return ProductService(product_repository=product_repository)
