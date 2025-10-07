from pydantic import BaseModel
from model.item import Item
from model.order import Order


class ItemInOrderResponse(BaseModel):
    item: Item
    amount_in_order: int
    total_price: float

