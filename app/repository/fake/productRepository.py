from collections import defaultdict

from fastapi import Depends

from domain.entities.compositionElement import CompositionELement
from domain.entities.product import Product, ProductFullInfo
from repository.abstractRepositroies import AbstractProductRepository

milk = CompositionELement(name="milk")
suggar = CompositionELement(name="sugar")
dough = CompositionELement(name="dough")
salt = CompositionELement(name="salt")

fake_products_list = [
    ProductFullInfo(
        product_id=1,
        product_image="/images/1",
        name="Kurabye Bisquits",
        composition=[milk, suggar, dough, salt],
        energy=100,
        price=10.99,
    ),
    ProductFullInfo(
        product_id=2,
        product_image="/images/2",
        name="Kurabye Cookies",
        energy=200,
        composition=[
            milk,
            suggar,
            dough,
        ],
        price=12.99,
    ),
    ProductFullInfo(
        product_id=3,
        product_image="/images/3",
        name="Kurabye Crackers",
        energy=300,
        composition=[milk, suggar, dough],
        price=14.99,
    ),
    ProductFullInfo(
        product_id=4,
        product_image="/images/4",
        name="Kurabye Cakes",
        energy=400,
        composition=[milk, suggar, dough],
        price=16.99,
    ),
    ProductFullInfo(
        product_id=5,
        product_image="/images/5",
        name="Kurabye Candies",
        energy=500,
        composition=[milk, suggar, dough],
        price=18.99,
    ),
    ProductFullInfo(
        product_id=6,
        product_image="/images/6",
        name="Kurabye Chocolates",
        energy=600,
        composition=[milk, suggar, dough],
        price=20.99,
    ),
]

fake_products: dict[int, Product | None] = defaultdict(lambda: None)
for product in fake_products_list:
    fake_products[product.product_id] = product


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: None):
        self.__session: None = session

    async def get_product(self, product_id: int) -> Product | None:
        return fake_products[product_id]

    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        return (
            [Product(**product.model_dump()) for product in fake_products_list[offset : offset + limit]]
            if fake_products_list
            else None
        )


get_session = lambda: None  # noqa: E731


def get_product_repository(session: None = Depends(get_session)):
    return ProductRepository(session=session)
