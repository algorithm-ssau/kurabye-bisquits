from fastapi import APIRouter

from api.v1.enpoints.auth import router as auth_router

routers = APIRouter()
routers_list = [
    auth_router,
]

for router in routers_list:
    router.tags.append("v1")
    routers.include_router(router)
