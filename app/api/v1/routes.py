from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.cart import router as cart_router
from api.v1.endpoints.product import router as product_router

routers = APIRouter()
routers_list = [
    auth_router,
    product_router,
    cart_router,
]

for router in routers_list:
    router.tags.append("v1")
    routers.include_router(router, prefix="/v1")
