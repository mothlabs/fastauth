from pydantic import BaseModel

from fastauth.models.user import FastUser


class RegisterUserRequest(BaseModel):
    email: str
    password: str


class RegisterUserResponse(BaseModel):
    user: FastUser
