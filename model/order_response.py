from datetime import datetime
from pydantic import BaseModel, Field
from model.item import Item
from model.user_response import UserResponse
from typing import List


class OrderResponse(BaseModel):
    Customer: UserResponse
    order_id: int = Field(alias="id")
    order_status: str
    order_date: datetime
    order_address: str
    total_price: float
    order_items: List[Item]
    item_amount: int
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True