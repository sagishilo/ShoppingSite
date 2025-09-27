from pydantic import BaseModel


class UserResponse (BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    user_name: str
