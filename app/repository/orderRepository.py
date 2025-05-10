from pathlib import Path

from fastapi import Depends
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import log_setting
from core.postgres import db_helper
from domain.entities.constants import DELIVERED, NO_STATUS
from domain.entities.order import CreateOrder, Order, OrderFullInfo, UpdateOrder
from repository.abstractRepositroies import AbstractOrderRepository
from repository.sql.orderQueries import (
    CREATE_ORDER,
    GET_ALL_ORDERS,
    GET_ORDER,
    PLACE_CART_ITEMS_TO_ORDER,
    SAFE_DELETE_ORDER,
    UPDATE_ORDER_STATUS,
)

log = log_setting.get_configure_logging(Path(__file__).stem)


class OrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create_order(
        self,
        order: CreateOrder,
    ) -> OrderFullInfo | None:  # TODO: remove None, raise error instead
        async with self.__session as session:
            try:
                db_order = await session.execute(
                    CREATE_ORDER,
                    params={
                        "user_id": order.user_id,
                        "shipping_address": order.shipping_adderess,
                        "status_id": order.status_id,
                        "order_comment": order.comment,
                    },
                )
                db_order = db_order.mappings().fetchone()
                log.info(db_order)
                await session.commit()
                if db_order:
                    return OrderFullInfo(order_id=db_order["order_id"], **order.model_dump())
                # TODO: raise error
            except DBAPIError as error:
                log.error("Error with creating order: %s (%s)", order, error)
                await session.rollback()
                # TODO: raise error

    async def set_order_items(self, cart_id: int, order_id: int) -> bool:
        """
        Transfer cart_items to the order_items (Insert to order_items and delete from cart_items atomically).
        """
        async with self.__session as session:
            try:
                await session.execute(
                    PLACE_CART_ITEMS_TO_ORDER,
                    params={"cart_id": cart_id, "order_id": order_id},
                )
                await session.commit()
                return True
            except DBAPIError as error:
                log.error(
                    "Error with adding items from cart %s to the order %s (Error: %s)",
                    cart_id,
                    order_id,
                    error,
                )
                await session.rollback()
                return False

        return False

    async def get_order(self, order_id: int) -> Order | None:
        async with self.__session as session:
            order = await session.execute(GET_ORDER, params={"order_id": order_id})
            order = order.mappings().fetchone()
            if order:
                order = Order(**order)
                return order
            return None

    async def get_all_orders(self, excepted_status_id: int = NO_STATUS) -> list[Order] | None:
        """
        Return all orders, excepted one of the status. If the excepted_status_id is note specified,
        it will be 0 (no status)
        """
        # TODO: REFORMAT THIS METHOD!
        async with self.__session as session:
            orders = await session.execute(GET_ALL_ORDERS, params={"excepted_status_id": excepted_status_id})
            orders = [Order(**order) for order in orders.mappings().fetchall()]
            log.info(orders)
            return orders if orders else None

    async def get_user_orders(
        self,
        user_id: int,
        status_id: int | None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Order] | None:
        """
        If status_id is None, the method will return all users orders.
        """
        pass

    async def update_order(self, order_id, update_order: UpdateOrder) -> Order | None:
        """In this realization this method allow to update only order status"""
        async with self.__session as session:
            try:
                order = await session.execute(
                    UPDATE_ORDER_STATUS,
                    params={
                        "order_id": update_order.order_id,
                        "status_id": update_order.status_id,
                    },
                )
                order = order.mappings().fetchone()

                return Order(**order) if order else None

            except DBAPIError:
                await session.rollback()
                log.warning(
                    "Failed update the order with id %s to the new status_id %s",
                    update_order.order_id,
                    update_order.status_id,
                )
                # TODO: raise exception

    async def delete_order(self, order_id: int) -> bool:
        async with self.__session as session:
            try:
                await session.execute(SAFE_DELETE_ORDER, params={"order_id": order_id})
                await session.commit()
                return True
            except DBAPIError:
                await session.rollback()
                log.warning("Failed with deliting the order with id %s", order_id)

        return False


def get_order_repository(session: AsyncSession = Depends(db_helper.get_session_dependency)):
    return OrderRepository(session=session)
