from pydantic import BaseModel
from datetime import datetime


class OrderSummary(BaseModel):
    order_id: int
    order_date: datetime
    order_address: str
    total_items: int
    total_price: float



