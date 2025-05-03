from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from schemas.product import ProductResponseSchema
from services.productService import ProductService, get_product_service

router = APIRouter(prefix="/product", tags=["Products"])


@router.get(
    "/",
    response_model=list[ProductResponseSchema],
    status_code=HTTPStatus.OK,
    responses={
        404: {"description": "The products has't founded."},
    },
)
async def get_products(product_service: ProductService = Depends(get_product_service)):
    products = await product_service.get_products(limit=5, offset=0)
    if products:
        return products

    return HTTPException(status_code=404, detail="The products has't founded.")
