from pydantic import BaseModel, Field


class Inventory(BaseModel):
    product_id: int
    warehouse_id: int
    stock_quantity: int
    warehouse_name: str | None = None
