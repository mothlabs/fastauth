import uuid

from beanie import Document
from pydantic import BaseModel, Field


class FastUser(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    email: str
    password: bytes = Field(exclude=True)
    access_token: str = Field(exclude=True)

    class Settings:
        name = "users"
