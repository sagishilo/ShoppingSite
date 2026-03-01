from pydantic import BaseModel


class ItemRequest (BaseModel):
    item_name: str
    price: float
    amount_in_stock: int
    image_url: str