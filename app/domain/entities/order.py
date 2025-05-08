from pydantic import BaseModel, Field, model_validator


class Order(BaseModel):
    order_id: int
    status_id: int
    user_id: int
    shipping_adderess: str
    comment: str | None = None


class UpdateOrderData(BaseModel):
    status_id: int | None = None
    shipping_adderess: str | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def check_at_least_one_field_seted(self):
        if not any((self.status_id, self.shipping_adderess, self.comment)):
            raise ValueError("At least one value should be setted for update")
        return self
