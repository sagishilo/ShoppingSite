from datetime import datetime
from pydantic import BaseModel
from model.item import Item
from model.user_response import UserResponse
from typing import List


class OrderResponse(BaseModel):
    Customer: UserResponse
    order_id: int
    order_date: datetime
    order_address: str
    total_price: float
    order_items: List[Item]
    item_amount: int
