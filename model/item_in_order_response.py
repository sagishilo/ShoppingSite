from pydantic import BaseModel
from model.item_response import ItemResponse


class ItemInOrderResponse(BaseModel):
    id: int
    item: ItemResponse
    amount_in_order: int
    total_price: float
    order_id: int

