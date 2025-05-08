from uuid import UUID

from fastapi import Depends

from core.postgres import db_helper
from domain.entities.compositionElement import CompositionELement
from domain.entities.product import Product, ProductFullInfo
from repository.abstractRepositroies import AbstractProductRepository

DEFAULT_LIMIT_VALUE = 10
DEFAUALT_OFFSET = 0


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: None):
        self.__session: None = session

    async def get_product(self, product_id: UUID) -> Product | None:
        pass

    async def get_products(
        self,
        limit: int = DEFAULT_LIMIT_VALUE,
        offset: int = DEFAUALT_OFFSET,
    ) -> list[Product] | None:
        pass


def get_product_repository(session: None = Depends(db_helper.get)):
    return ProductRepository(session=session)
