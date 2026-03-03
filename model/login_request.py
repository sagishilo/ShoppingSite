from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_name: str
    password: str