from datetime import datetime
from pydantic import BaseModel
from model.order_status import OrderStatus


class OrderRequest(BaseModel):
    buyer_id: int
    order_date: datetime
    order_address: str
    order_status: OrderStatus