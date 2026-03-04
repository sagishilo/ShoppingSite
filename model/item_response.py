from pydantic import BaseModel


class ItemResponse (BaseModel):
    id: int
    item_name: str
    price: float
    image_url: str
