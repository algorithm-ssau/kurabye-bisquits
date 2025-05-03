from uuid import UUID

from fastapi import Depends
from sqlalchemy.util import defaultdict

from domain.entities.product import Product
from repository.abstractRepositroies import AbstractProductRepository

fake_products_list = [
    Product(
        product_id=UUID("fcb26434-d665-42d0-a647-db2b8d6a8e05"),
        product_image="/images/1",
        name="Kurabye Bisquits",
        price=10.99,
    ),
    Product(
        product_id=UUID("fcb26434-d665-42d0-a647-db2b8d6a8e06"),
        product_image="/images/2",
        name="Kurabye Cookies",
        price=12.99,
    ),
    Product(
        product_id=UUID("fcb26434-d665-42d0-a647-db2b8d6a8e07"),
        product_image="/images/3",
        name="Kurabye Crackers",
        price=14.99,
    ),
    Product(
        product_id=UUID("fcb26434-d665-42d0-a647-db2b8d6a8e08"),
        product_image="/images/4",
        name="Kurabye Cakes",
        price=16.99,
    ),
    Product(
        product_id=UUID("fcb26434-d665-42d0-a647-db2b8d6a8e09"),
        product_image="/images/5",
        name="Kurabye Candies",
        price=18.99,
    ),
    Product(
        product_id=UUID("fcb26434-d665-42d0-a647-db2b8d6a8e10"),
        product_image="/images/6",
        name="Kurabye Chocolates",
        price=20.99,
    ),
]

fake_products: dict[UUID, Product | None] = defaultdict(None)
for product in fake_products_list:
    fake_products[product.product_id] = product


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: None):
        self.__session: None = session

    async def get_product(self, product_id: UUID) -> Product | None:
        return fake_products[product_id]

    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        return fake_products_list[offset : offset + limit] if fake_products_list else None


get_session = lambda: None  # noqa: E731


def get_product_repository(session: None = Depends(get_session)):
    return ProductRepository(session=session)
