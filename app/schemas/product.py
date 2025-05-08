from pydantic import BaseModel, Field

from domain.enums import ProductCalculus


class ProductResponseSchema(BaseModel):
    product_id: int
    name: str = Field(min_length=1, max_length=255)
    product_image: str
    price: float
    calculus: ProductCalculus = Field(default=ProductCalculus.IN_GRAMS)
    grammage: int | None = Field(gt=0, default=None)

    def __hash__(self):
        return hash(self.product_id)


class ProductFullResponseSchema(ProductResponseSchema):
    description: str | None = Field(default=None, description="The information about the project.")
    composition: list = Field(description="The composition of the product, e.g.: milk, sugar and etc.")
    energy: int = Field(description="The energy of the product of the 100 grams, e.g. 100kCal")
    fats: int = Field(default=0)
    carbohydrates: int = Field(default=0)
    proteins: int = Field(default=0)


class ProductListQueryParams(BaseModel):
    limit: int = Field(default=12, gt=0, le=25, description="Limit of the products on the page.")
    offset: int = Field(default=0, ge=0, description="Offset of the for products for the pagination.")
    sorting_by: str | None = Field(default=None, description="The rule of sorting the elements.")
    sorting_order: str = Field(
        pattern=r"^(asc|desc)$",
        default="asc",
        description="The sorting order, asc — from the least to the gretest, desc — from the greatest to the least.",
    )


class ProductQueryParams(BaseModel):
    product_id: int
    package_id: int
