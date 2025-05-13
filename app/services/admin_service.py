from typing import List, Optional

from fastapi import Depends

from domain.entities.inventory import Inventory
from domain.entities.order import Order
from domain.entities.product import Product, ProductFullInfo
from repository.admin_repository import AdminRepository, get_admin_repository


class AdminService:
    def __init__(self, repository: AdminRepository):
        self.repository = repository

    async def get_products(self, limit: int, offset: int) -> list[Product] | None:
        return await self.repository.get_products(limit=limit, offset=offset)

    async def get_product(self, product_id: int) -> ProductFullInfo | None:
        return await self.repository.get_product(product_id=product_id)

    async def update_product(self, product: ProductFullInfo) -> ProductFullInfo | None:
        return await self.repository.update_product(product=product)

    async def get_inventory(self) -> list[Inventory] | None:
        return await self.repository.get_inventory()

    async def delete_inventory(self, product_id: int, warehouse_id: int) -> bool:
        return await self.repository.delete_inventory(product_id=product_id, warehouse_id=warehouse_id)

    async def upsert_inventory(self, product_id: int, warehouse_id: int, stock_quantity: int) -> bool:
        return await self.repository.upsert_inventory(
            product_id=product_id, warehouse_id=warehouse_id, stock_quantity=stock_quantity
        )

    async def get_orders(self, limit: int, offset: int) -> list[Order] | None:
        return await self.repository.get_orders(limit=limit, offset=offset)

    async def update_order_status(self, order_id: int, status_id: int) -> bool:
        return await self.repository.update_order_status(order_id=order_id, status_id=status_id)


def get_admin_service(repository: AdminRepository = Depends(get_admin_repository)):
    return AdminService(repository=repository)
