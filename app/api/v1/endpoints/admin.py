from http import HTTPStatus

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from core.config import auth_settings, log_setting
from domain.entities.inventory import Inventory
from domain.entities.product import ProductFullInfo
from domain.entities.user import User
from schemas.inventory_schemas import InventoryResponseSchema
from schemas.order_schemas import OrderResponseSchema
from schemas.product import ProductFullResponseSchema, ProductListQueryParams, ProductResponseSchema
from schemas.token import TokenResponseSchema
from services.admin_service import AdminService, get_admin_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")
ADMIN_ROLE_ID = 2
SECRET_KEY = auth_settings.secret_key
ALGORITHM = auth_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = auth_settings.access_token_expire_minutes


async def admin_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = User(**payload)
        if user.role_id != ADMIN_ROLE_ID:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions: Admin role required"
            )
        return user
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions: Admin role required"
        )


router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(admin_route)])
log = log_setting.get_configure_logging(filename=__name__)


@router.get(
    "/products",
    response_model=list[ProductResponseSchema],
    status_code=HTTPStatus.OK,
    responses={404: {"description": "No products found."}},
)
async def get_products(
    query: ProductListQueryParams = Query(),
    admin_service: AdminService = Depends(get_admin_service),
):
    products = await admin_service.get_products(limit=query.limit, offset=query.offset)
    if products:
        return products
    raise HTTPException(status_code=404, detail="No products found.")


@router.get(
    "/products/{product_id}",
    response_model=ProductFullResponseSchema,
    status_code=HTTPStatus.OK,
    responses={404: {"description": "Product not found."}},
)
async def get_product(
    product_id: int,
    admin_service: AdminService = Depends(get_admin_service),
):
    product = await admin_service.get_product(product_id=product_id)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found.")


@router.put(
    "/products/{product_id}",
    response_model=ProductFullResponseSchema,
    status_code=HTTPStatus.OK,
    responses={404: {"description": "Failed to update product."}},
)
async def update_product(
    product_id: int,
    product: ProductFullInfo,
    admin_service: AdminService = Depends(get_admin_service),
):
    product.product_id = product_id
    updated_product = await admin_service.update_product(product=product)
    if updated_product:
        return updated_product
    raise HTTPException(status_code=404, detail="Failed to update product.")


@router.get(
    "/inventory",
    response_model=list[InventoryResponseSchema],
    status_code=HTTPStatus.OK,
    responses={404: {"description": "No inventory found."}},
)
async def get_inventory(
    admin_service: AdminService = Depends(get_admin_service),
):
    inventory = await admin_service.get_inventory()
    if inventory:
        return inventory
    raise HTTPException(status_code=404, detail="No inventory found.")


@router.delete(
    "/inventory/{product_id}/{warehouse_id}",
    status_code=HTTPStatus.NO_CONTENT,
    responses={404: {"description": "Failed to delete inventory."}},
)
async def delete_inventory(
    product_id: int,
    warehouse_id: int,
    admin_service: AdminService = Depends(get_admin_service),
):
    success = await admin_service.delete_inventory(product_id=product_id, warehouse_id=warehouse_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failed to delete inventory.")


@router.post(
    "/inventory", status_code=HTTPStatus.CREATED, responses={400: {"description": "Failed to update inventory."}}
)
async def upsert_inventory(
    inventory: Inventory,
    admin_service: AdminService = Depends(get_admin_service),
):
    success = await admin_service.upsert_inventory(
        product_id=inventory.product_id, warehouse_id=inventory.warehouse_id, stock_quantity=inventory.stock_quantity
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update inventory.")


@router.get(
    "/orders",
    response_model=list[OrderResponseSchema],
    status_code=HTTPStatus.OK,
    responses={404: {"description": "No orders found."}},
)
async def get_orders(
    query: ProductListQueryParams = Query(),
    admin_service: AdminService = Depends(get_admin_service),
):
    orders = await admin_service.get_orders(limit=query.limit, offset=query.offset)
    if orders:
        return orders
    raise HTTPException(status_code=404, detail="No orders found.")


@router.patch(
    "/orders/{order_id}/status",
    status_code=HTTPStatus.NO_CONTENT,
    responses={404: {"description": "Failed to update order status."}},
)
async def update_order_status(
    order_id: int,
    status_id: int,
    admin_service: AdminService = Depends(get_admin_service),
):
    success = await admin_service.update_order_status(order_id=order_id, status_id=status_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failed to update order status.")
