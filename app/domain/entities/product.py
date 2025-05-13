from pydantic import BaseModel, Field

from domain.enums import ProductCalculus


class Product(BaseModel):
    product_id: int
    name: str = Field(min_length=1, max_length=255)
    product_image: str
    price: float
    calculus: ProductCalculus = Field(default=ProductCalculus.IN_GRAMS)
    grammage: int | None = Field(gt=0, default=None)

    def __hash__(self):
        return hash(self.product_id)


class ProductFullInfo(Product):
    description: str | None = Field(default=None, description="The information about the project.")
    composition: list = Field(description="The composition of the product, e.g.: milk, sugar and etc.")
    energy: int | None = Field(description="The energy of the product of the 100 grams, e.g. 100kCal")
    fats: int = Field(default=0)
    carbohydrates: int = Field(default=0)
    is_active: bool = True
    proteins: int = Field(default=0)


class UpdateProduct(BaseModel):
    product_id: int
    name: str | None = Field(min_length=1, max_length=255, default=None)
    product_image: str | None = None
    price: float | None = None
    calculus: ProductCalculus | None = Field(default=ProductCalculus.IN_GRAMS)
    grammage: int | None = Field(gt=0, default=None)
    description: str | None = Field(default=None, description="The information about the project.")
    composition: list | None = Field(
        default=None, description="The composition of the product, e.g.: milk, sugar and etc."
    )
    energy: int | None = Field(default=None, description="The energy of the product of the 100 grams, e.g. 100kCal")
    fats: int | None = Field(default=None)
    carbohydrates: int | None = Field(default=None)
    proteins: int | None = Field(default=None)
