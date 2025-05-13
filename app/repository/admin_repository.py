from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import log_setting
from core.postgres import db_helper
from domain.entities.compositionElement import CompositionELement
from domain.entities.inventory import Inventory
from domain.entities.order import Order
from domain.entities.product import Product, ProductFullInfo

log = log_setting.get_configure_logging(filename=__name__)

# SQL Queries
SELECT_ADMIN_PRODUCTS = text(
    """
    SELECT
        product_id,
        created_at,
        updated_at,
        product_image,
        product_name as name,
        grammage,
        product_price as price,
        is_active
    FROM product
    ORDER BY product_name
    LIMIT :limit
    OFFSET :offset;
    """
)

SELECT_ADMIN_PRODUCT_DETAILS = text(
    """
    SELECT
        p.product_id,
        p.product_name,
        p.product_image,
        p.grammage,
        p.product_price,
        p.is_active,
        md.description,
        md.fats,
        md.proteins,
        md.carbohydrates,
        ((proteins * 4 + carbohydrates * 4 + fats * 9)*grammage/100)::int as energy,
        jsonb_agg(
            jsonb_build_object(
                'element_id', ingredient_id,
                'name', ingredient_name,
                'is_allergen', is_allergen
            )
        ) as composition
    FROM product p
    JOIN md_product md USING(product_id)
    LEFT JOIN product_composition pc USING(product_id)
    LEFT JOIN ingredient i USING(ingredient_id)
    WHERE p.product_id = :product_id
    GROUP BY p.product_id, md.description, md.fats, md.proteins, md.carbohydrates;
    """
)

UPDATE_ADMIN_PRODUCT = text(
    """
    with update_product as(
    UPDATE product
    SET
        product_name = :product_name,
        product_image = :product_image,
        grammage = :grammage,
        product_price = :product_price,
        is_active = :is_active,
        updated_at = current_timestamp
    WHERE product_id = :product_id
    ), update_md_product as (
    UPDATE md_product
    SET
        description = :description,
        fats = :fats,
        proteins = :proteins,
        carbohydrates = :carbohydrates
    WHERE product_id = :product_id
    )
    select true;
    """
)

SELECT_INVENTORY = text(
    """
    SELECT
        product_id,
        warehouse_id,
        stock_quantity,
        warehouse_name
    FROM inventory
    JOIN warehouse USING(warehouse_id)
    """
)

DELETE_INVENTORY = text(
    """
    DELETE FROM inventory
    WHERE product_id = :product_id
    AND warehouse_id = :warehouse_id;
    """
)

UPSERT_INVENTORY = text(
    """
    INSERT INTO inventory (product_id, warehouse_id, stock_quantity)
    VALUES (:product_id, :warehouse_id, :stock_quantity)
    ON CONFLICT (product_id, warehouse_id)
    DO UPDATE SET stock_quantity = inventory.stock_quantity + excluded.stock_quantity;
    """
)

SELECT_ORDERS = text(
    """
    SELECT
        order_id,
        created_at,
        updated_at,
        user_id,
        shipping_address,
        status_id,
        order_comment
    FROM "order"
    ORDER BY created_at DESC
    LIMIT :limit
    OFFSET :offset;
    """
)

UPDATE_ORDER_STATUS = text(
    """
    UPDATE "order"
    SET
        status_id = :status_id,
        updated_at = current_timestamp
    WHERE order_id = :order_id;
    """
)


class AbstractAdminRepository(ABC):
    @abstractmethod
    async def get_products(self, limit: int, offset: int) -> list[Product] | None:
        pass

    @abstractmethod
    async def get_product(self, product_id: int) -> ProductFullInfo | None:
        pass

    @abstractmethod
    async def update_product(self, product: ProductFullInfo) -> ProductFullInfo | None:
        pass

    @abstractmethod
    async def get_inventory(self) -> list[Inventory] | None:
        pass

    @abstractmethod
    async def delete_inventory(self, product_id: int, warehouse_id: int) -> bool:
        pass

    @abstractmethod
    async def upsert_inventory(self, product_id: int, warehouse_id: int, stock_quantity: int) -> bool:
        pass

    @abstractmethod
    async def get_orders(self, limit: int, offset: int) -> list[Order] | None:
        pass

    @abstractmethod
    async def update_order_status(self, order_id: int, status_id: int) -> bool:
        pass


class AdminRepository(AbstractAdminRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_products(self, limit: int = 10, offset: int = 0) -> list[Product] | None:
        async with self.__session as session:
            result = await session.execute(SELECT_ADMIN_PRODUCTS, params={"limit": limit, "offset": offset})
            products = result.mappings().fetchall()

            if products:
                return [Product(**product) for product in products]
            return None

    async def get_product(self, product_id: int) -> ProductFullInfo | None:
        async with self.__session as session:
            result = await session.execute(SELECT_ADMIN_PRODUCT_DETAILS, params={"product_id": product_id})
            db_product = result.mappings().fetchone()

            if db_product:
                compositions = [CompositionELement(**element) for element in db_product["composition"]]
                product = ProductFullInfo(
                    product_id=db_product["product_id"],
                    name=db_product["product_name"],
                    product_image=db_product["product_image"],
                    grammage=db_product["grammage"],
                    price=db_product["product_price"],
                    description=db_product["description"],
                    fats=db_product["fats"],
                    proteins=db_product["proteins"],
                    carbohydrates=db_product["carbohydrates"],
                    composition=compositions,
                    energy=db_product["energy"],
                    is_active=db_product["is_active"],
                )
                log.info("Retrieved admin product: %s", product)
                return product
            return None

    async def update_product(self, product: ProductFullInfo) -> ProductFullInfo | None:
        async with self.__session as session:
            try:
                await session.begin()
                await session.execute(
                    UPDATE_ADMIN_PRODUCT,
                    params={
                        "product_id": product.product_id,
                        "product_name": product.name,
                        "product_image": product.product_image,
                        "grammage": product.grammage,
                        "product_price": product.price,
                        "is_active": product.is_active,
                        "description": product.description,
                        "fats": product.fats,
                        "proteins": product.proteins,
                        "carbohydrates": product.carbohydrates,
                    },
                )
                await session.commit()
                log.info("Updated product: %s", product.product_id)
                return product
            except DBAPIError as e:
                await session.rollback()
                log.error("Failed to update product %s: %s", product.product_id, str(e))
                return None

    async def get_inventory(self) -> list[Inventory] | None:
        async with self.__session as session:
            result = await session.execute(SELECT_INVENTORY)
            inventory = result.mappings().fetchall()

            if inventory:
                return [Inventory(**item) for item in inventory]
            return None

    async def delete_inventory(self, product_id: int, warehouse_id: int) -> bool:
        async with self.__session as session:
            try:
                await session.begin()
                await session.execute(DELETE_INVENTORY, params={"product_id": product_id, "warehouse_id": warehouse_id})
                await session.commit()
                log.info("Deleted inventory for product %s, warehouse %s", product_id, warehouse_id)
                return True
            except DBAPIError as e:
                await session.rollback()
                log.error("Failed to delete inventory: %s", str(e))
                return False

    async def upsert_inventory(self, product_id: int, warehouse_id: int, stock_quantity: int) -> bool:
        async with self.__session as session:
            try:
                await session.begin()
                await session.execute(
                    UPSERT_INVENTORY,
                    params={"product_id": product_id, "warehouse_id": warehouse_id, "stock_quantity": stock_quantity},
                )
                await session.commit()
                log.info("Upserted inventory for product %s, warehouse %s", product_id, warehouse_id)
                return True
            except DBAPIError as e:
                await session.rollback()
                log.error("Failed to upsert inventory: %s", str(e))
                return False

    async def get_orders(self, limit: int = 10, offset: int = 0) -> list[Order] | None:
        async with self.__session as session:
            result = await session.execute(SELECT_ORDERS, params={"limit": limit, "offset": offset})
            orders = result.mappings().fetchall()

            if orders:
                return [Order(**order) for order in orders]
            return None

    async def update_order_status(self, order_id: int, status_id: int) -> bool:
        async with self.__session as session:
            try:
                await session.begin()
                result = await session.execute(
                    UPDATE_ORDER_STATUS, params={"order_id": order_id, "status_id": status_id}
                )
                await session.commit()
                log.info("Updated order %s status to %s", order_id, status_id)
                return True
            except DBAPIError as e:
                await session.rollback()
                log.error("Failed to update order status: %s", str(e))
                return False


def get_admin_repository(session: AsyncSession = Depends(db_helper.get_session_dependency)):
    return AdminRepository(session=session)
