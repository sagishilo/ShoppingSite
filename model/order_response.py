from datetime import datetime
from pydantic import BaseModel, Field
from model.item import Item
from model.item_in_order_response import ItemInOrderResponse
from model.user_response import UserResponse
from typing import List


class OrderResponse(BaseModel):
    customer: UserResponse
    id: int
    order_status: str
    order_date: datetime
    order_address: str
    order_items: List[ItemInOrderResponse]
    total_price: float
    item_amount: int