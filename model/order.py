from typing import Optional
from pydantic import BaseModel
import datetime
from model.order_status import OrderStatus


class Order(BaseModel):
    order_id: Optional[int]
    buyer_id: int
    order_date: datetime
    order_address: str
    order_status: OrderStatus



