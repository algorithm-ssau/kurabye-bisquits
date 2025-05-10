from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from sqlalchemy.util import defaultdict

from domain.entities.product import Product


class Order(BaseModel):
    order_id: int
    status_id: int
    user_id: int
    created_at: datetime
    shipping_address: str
    comment: str | None = None


class CreateOrder(BaseModel):
    status_id: int | None
    user_id: int
    created_at: datetime
    shipping_adderess: str
    comment: str | None = None


class OrderFullInfo(Order):
    product_list: defaultdict[Product, int] = defaultdict(lambda: 1)


class UpdateOrder(BaseModel):
    order_id: int
    status_id: int | None = None
    shipping_adderess: str | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def check_at_least_one_field_seted(self):
        if not any((self.status_id, self.shipping_adderess, self.comment)):
            raise ValueError("At least one value should be setted for update")
        return self
