from fastapi import APIRouter, FastAPI

from fastauth.models.user import FastUser
from fastauth.services import AuthenticationService


class FastAuth:
    def __init__(
        self,
        user_model: FastUser,
        prefix: str = "/auth",
        tags: list[str] | None = None,
    ) -> None:
        self.user_model = user_model
        self.router = APIRouter(prefix=prefix, tags=tags or ["auth"])
        self.service = AuthenticationService()

    def register(self, app: FastAPI) -> None:
        app.include_router(self.router)
