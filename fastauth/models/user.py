import uuid

from beanie import Document
from pydantic import Field
from redis_om import Field as OMField
from redis_om import HashModel


class FastUser(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    email: str
    password: bytes = Field(exclude=True)
    access_token: str = Field(exclude=True)

    authenticated: bool = False

    class Settings:
        name = "users"


class CachedUser(HashModel):
    authenticated: int = 0
    id: str = OMField(index=True)
    access_token: str = OMField(index=True)
