from pydantic import BaseModel


class RegisterUserRequest(BaseModel):
    email: str
    password: str
