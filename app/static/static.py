from fastapi import APIRouter, Request, responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Static"])


templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/product/{product_id}", response_class=HTMLResponse)
async def get_product(product_id: int, request: Request):
    return templates.TemplateResponse("ovsyanoe.html", {"request": request})


@router.get("/basket.html", response_class=HTMLResponse)
@router.get("/basket", response_class=HTMLResponse)
async def get_bassket(request: Request):
    return templates.TemplateResponse("basket.html", {"request": request})


@router.get("/login.html")
@router.get("/login", response_class=HTMLResponse)
async def get_auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.get("/profile.html", response_class=HTMLResponse)
@router.get("/profile", response_class=HTMLResponse)
async def get_profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/order.html", response_class=HTMLResponse)
@router.get("/order")
async def get_order_page(request: Request):
    return templates.TemplateResponse("order.html", {"request": request})


@router.get("/order.html/{order_id_path}", response_class=HTMLResponse)
@router.get("/order/{order_id_path}")
async def get_same_order_page(order_id_path: int, request: Request):
    return templates.TemplateResponse("order-detail.html", {"request": request, "order_id": order_id_path})


@router.get("/admin/", response_class=HTMLResponse)
@router.get("/admin/")
async def get_admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
