from typing import Optional
from pydantic import BaseModel


class Item (BaseModel):
    id: Optional[int]
    item_name: str
    price: float
    amount_in_stock: int
