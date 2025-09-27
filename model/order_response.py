from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from model.item import Item


class OrderResponse(BaseModel):
    order_id: Optional[int]
    buyer_name: int
    order_date: datetime
    order_address: str
    total_price: float
    order_items: list[Item]
    item_amount: int
