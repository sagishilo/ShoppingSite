from pydantic import BaseModel


class ItemResponse (BaseModel):
    item_name: str
    price: float
