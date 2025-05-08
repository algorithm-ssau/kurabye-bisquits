from collections import defaultdict
from pathlib import Path

from fastapi import Depends
from sqlalchemy.exc import DataError, DBAPIError
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.config import log_setting
from core.postgres import db_helper
from domain.entities.cart import Cart
from domain.entities.product import Product
from domain.exceptions.cartExceptions import CartDeleteError, CartInsertError
from repository.abstractRepositroies import AbstractCartRepository
from repository.sql.cartQueries import (
    DELETE_ALL_PRODUCTS,
    DELETE_QUANTITY_OF_PRODUCT,
    SELECT_CART_ITEMS,
    UPSERT_PRODUCT_IN_CART,
)

log = log_setting.get_configure_logging(Path(__file__).stem)


class CartRepository(AbstractCartRepository):
    def __init__(self, session: AsyncSession):
        self.__session: AsyncSession = session

    async def add_product_to_cart(
        self,
        cart_id: int,
        product_id: int,
        product_quantity: int = 1,
    ) -> bool:
        async with self.__session as session:
            try:
                await session.execute(
                    UPSERT_PRODUCT_IN_CART,
                    params={
                        "cart_id": cart_id,
                        "product_id": product_id,
                        "quantity": product_quantity,
                    },
                )
                await session.commit()
                return True

            except DBAPIError as error:
                await session.rollback()
                raise CartInsertError("Cart or product doesn't exists") from error

        await session.rollback()
        return False

    async def delete_product_from_cart(
        self,
        cart_id: int,
        product_id,
        product_quantity: None | int = None,
    ) -> bool:
        #  if product quantity doesn't specified, thats means
        #  that we should delete all product from the cart
        delete_all = product_quantity is None

        async with self.__session as session:
            try:
                if delete_all:
                    await session.execute(
                        DELETE_ALL_PRODUCTS,
                        params={
                            "cart_id": cart_id,
                            "product_id": product_id,
                        },
                    )
                else:
                    await session.execute(
                        DELETE_QUANTITY_OF_PRODUCT,
                        params={
                            "cart_id": cart_id,
                            "product_id": product_id,
                            "quantity_to_delete": product_quantity,
                        },
                    )
                await session.commit()
                return True

            except DBAPIError as error:
                await session.rollback()
                raise CartDeleteError("Cart or product doesn't exists.") from error

        return False

    async def get_cart(self, cart_id: int) -> Cart | None:
        async with self.__session as session:
            cart_items_db = await session.execute(
                SELECT_CART_ITEMS,
                params={"cart_id": cart_id},
            )
            cart_items_db = cart_items_db.mappings().fetchone()

        if cart_items_db:
            # key — Rroduct (it is hashable), value — quantity of items in the cart
            cart_items: dict[Product, int] = defaultdict(lambda: 1)
            for cart_item in cart_items_db["products"]:
                # take product from the db_cart and put it in the cart
                product = Product(**cart_item)
                cart_items[product] = cart_item["quantity"]

            log.debug("Items in the cart %s: %s", cart_items_db["cart_id"], cart_items)

            # create model of the cart
            cart = Cart(cart_id=cart_id, cart_items=cart_items)
            return cart

        return None


def get_cart_repository(
    session: AsyncSession = Depends(db_helper.get_session_dependency),
) -> AbstractCartRepository:
    return CartRepository(session=session)
