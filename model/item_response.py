from typing import Optional
from pydantic import BaseModel


class ItemResponse (BaseModel):
    item_name: str
    price: float
    amount_in_stock: int
