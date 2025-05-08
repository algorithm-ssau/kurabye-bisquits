from pydantic import BaseModel, Field


class Order(BaseModel):
    order_id: int
    status_id: int
    user_id: int
    shipping_adderess: str
    comment: str | None = None
