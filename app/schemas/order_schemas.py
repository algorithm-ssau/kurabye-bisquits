from datetime import datetime

from pydantic import BaseModel, Field


class Order(BaseModel):
    order_id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    shipping_address: str
    status_id: int
    order_comment: str | None = None


class OrderResponseSchema(BaseModel):
    order_id: int
    created_at: datetime
    user_id: int
    shipping_address: str
    status_id: int
    order_comment: str | None = None
