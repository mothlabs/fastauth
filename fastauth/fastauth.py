from typing import Type

from fastapi import APIRouter, FastAPI
from loguru import logger

from fastauth.models.schemas import RegisterUserRequest, RegisterUserResponse
from fastauth.models.user import FastUser
from fastauth.services import AuthenticationService


class FastAuth:
    def __init__(
        self,
        user_model: Type[FastUser],
        prefix: str = "/auth",
        tags: list[str] | None = None,
    ) -> None:
        self.user_model = user_model
        self.router = APIRouter(prefix=prefix, tags=tags or ["auth"])
        self.service = AuthenticationService(user_model=user_model)

    def register(self, app: FastAPI) -> None:
        self._register_routers()
        app.include_router(self.router)

    def _register_routers(self) -> None:

        @self.router.post("/register")
        async def register(body: RegisterUserRequest) -> RegisterUserResponse:

            user = self.service.register_user(
                **body.model_dump_json(),
            )

            return RegisterUserResponse(user=user)

        logger.info(f"Registered routers for FastAuth at '{self.router.prefix}'")
