from typing import Optional
from pydantic import BaseModel


class UserRequest (BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    user_name: str
    password: str
