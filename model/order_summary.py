from pydantic import BaseModel
from datetime import datetime


class OrderSummary(BaseModel):
    order_id: int
    order_date: datetime
    total_items: int
    total_price: float



