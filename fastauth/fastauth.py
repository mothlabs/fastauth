from fastapi import APIRouter, FastAPI

from fastauth.models.user import FastUser


class FastAuth:
    def __init__(
        self,
        user_model: FastUser,
        prefix: str = "/auth",
        tags: list[str] | None = None,
    ) -> None:
        self.user_model = user_model
        self.router = APIRouter(prefix=prefix, tags=tags or ["auth"])

    def register(self, app: FastAPI):
        app.include_router(self.router)
