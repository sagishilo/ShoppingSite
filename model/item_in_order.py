from typing import Optional
from pydantic import BaseModel


class ItemInOrder(BaseModel):
    id: Optional[int]=None
    order_id: int
    item_id: int
    amount_in_order: int