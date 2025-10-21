from typing import Optional
from pydantic import BaseModel
from datetime import date
from model.order_status import OrderStatus


class Order(BaseModel):
    id: Optional[int]
    buyer_id: int
    order_date: date
    order_address: str
    order_status: OrderStatus



