from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.product import ProductFullResponseSchema, ProductQueryParams, ProductResponseSchema
from services.productService import ProductService, get_product_service

router = APIRouter(prefix="/product", tags=["Products"])


@router.get(
    "/",
    response_model=list[ProductResponseSchema],
    status_code=HTTPStatus.OK,
    responses={
        404: {"description": "The products hasn't founded."},
    },
)
async def get_products(
    product_query: ProductQueryParams = Query(),
    product_service: ProductService = Depends(get_product_service),
):
    products = await product_service.get_products(limit=product_query.limit, offset=product_query.offset)
    if products:
        return products

    raise HTTPException(status_code=404, detail="The products hasn't founded.")


@router.get("/{product_id}", response_model=ProductFullResponseSchema)
async def get_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service),
):
    product = await product_service.get_product(product_id)
    if product:
        return product

    raise HTTPException(status_code=404, detail="The product hasn't founded.")
