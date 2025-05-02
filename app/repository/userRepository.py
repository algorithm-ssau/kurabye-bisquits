from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.postgres import db_helper
from domain.entities.product import Product
from repository.abstractRepositroies import AbstractProductRepository


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.__session: AsyncSession = session

    async def get_product(self, product_id: UUID) -> Product | None:
        pass

    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        pass


def get_user_repository(self, session: AsyncSession = Depends(db_helper.session_dependency)):
    return ProductRepository(session=session)
