from datetime import datetime

from pydantic import BaseModel


class CreateOrderSchema(BaseModel):
    status_id: int | None
    user_id: int
    created_at: datetime
    shipping_address: str
    comment: str | None = None
