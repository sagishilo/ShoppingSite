from typing import Optional
from pydantic import BaseModel


class Item (BaseModel):
    item_id: Optional[int]
    item_name: str
    price: float
    amount_in_stock: int
