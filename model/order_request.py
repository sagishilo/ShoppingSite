from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from model.order_status import OrderStatus


class OrderRequest(BaseModel):
    buyer_id: int
    order_date: datetime
    order_address: Optional[str]
    order_status: OrderStatus