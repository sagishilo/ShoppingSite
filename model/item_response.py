from pydantic import BaseModel


class ItemResponse (BaseModel):
    id: int
    item_name: str
    price: float
    amount_in_stock: int
    image_url: str
