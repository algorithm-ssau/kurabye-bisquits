from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import log_setting
from core.postgres import db_helper
from domain.entities.compositionElement import CompositionELement
from domain.entities.product import Product, ProductFullInfo
from domain.exceptions.productExceptions import ProductNotFoundException
from repository.abstractRepositroies import AbstractProductRepository
from repository.sql.productQueries import SELECT_ALL_RPODUCT_INFORMATION, SELECT_PRODUCTS

DEFAULT_LIMIT_VALUE = 10
DEFAUALT_OFFSET = 0

log = log_setting.get_configure_logging(filename=__name__)


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.__session: AsyncSession = session

    async def get_product(self, product_id: int, package_id: int) -> ProductFullInfo | None:
        async with self.__session as session:
            # get product from db
            db_product = await session.execute(
                SELECT_ALL_RPODUCT_INFORMATION,
                params={
                    "product_id": product_id,
                    "package_id": package_id,
                },
            )
            db_product = db_product.mappings().fetchone()
            log.debug("%s", db_product)
            if db_product:
                # create list of compositions of the product
                compositions = [CompositionELement(**element) for element in db_product["composition"]]
                # create product
                product = ProductFullInfo(
                    product_id=db_product["product_id"],
                    name=db_product["product_name"],
                    energy=db_product["energy"],
                    price=db_product["product_price"],
                    product_image=db_product["product_image"],
                    description=db_product["description"],
                    quantity=db_product["grammage"],
                    carbohydrates=db_product["carbohydrates"],
                    composition=compositions,
                )
                log.info("Open product: %s", product)
                return product

            return None

    async def get_products(
        self, limit: int = DEFAULT_LIMIT_VALUE, offset: int = DEFAUALT_OFFSET, order_by: str = "created at"
    ) -> list[Product] | None:
        async with self.__session as session:
            products = await session.execute(
                SELECT_PRODUCTS,
                params={
                    "limit": limit,
                    "offset": offset,
                    "order_by": order_by,
                },
            )
            products = products.mappings().fetchall()

        if products:
            return [Product(**product) for product in products]

        return None


def get_product_repository(session: AsyncSession = Depends(db_helper.get_session_dependency)):
    return ProductRepository(session=session)
