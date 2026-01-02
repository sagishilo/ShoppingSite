from pydantic import BaseModel
from model.item import Item
from model.item_response import ItemResponse
from model.order import Order


class ItemInOrderResponse(BaseModel):
    item: ItemResponse
    amount_in_order: int
    total_price: float
    order_id: int

