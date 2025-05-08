from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import log_setting
from schemas.product import ProductFullResponseSchema, ProductListQueryParams, ProductQueryParams, ProductResponseSchema
from services.productService import ProductService, get_product_service

router = APIRouter(prefix="/product", tags=["Products"])
log = log_setting.get_configure_logging(filename=__name__)


@router.get(
    "/all",
    response_model=list[ProductResponseSchema],
    status_code=HTTPStatus.OK,
    responses={
        404: {"description": "The products hasn't found."},
    },
)
async def get_products(
    product_query: ProductListQueryParams = Query(),
    product_service: ProductService = Depends(get_product_service),
):
    log.debug("Get product routes")
    products = await product_service.get_products(limit=product_query.limit, offset=product_query.offset)
    if products:
        return products

    log.warning(
        "There are no product founds in the database. Parametrs: limit %s offset %s",
        product_query.limit,
        product_query.offset,
    )
    raise HTTPException(status_code=404, detail="The products hasn't found.")


@router.get("/", response_model=ProductFullResponseSchema)
async def get_product(
    product_query: ProductQueryParams = Query(),
    product_service: ProductService = Depends(get_product_service),
):
    product = await product_service.get_product(
        product_id=product_query.product_id,
        package_id=product_query.package_id,
    )
    if product:
        return product

    raise HTTPException(status_code=404, detail="The product hasn't found.")
