import datetime as dt

from pydantic import BaseModel, Field

from fastauth import FastUser


class Profile(BaseModel):
    name: str | None = None
    bio: str | None = None
    birthdate: dt.datetime | None = None


class User(FastUser):
    profile: Profile = Field(default_factory=Profile)

    class Settings:
        name = "users"
