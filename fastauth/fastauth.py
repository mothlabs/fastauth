from typing import Callable, Coroutine, Type

from fastapi import APIRouter, FastAPI
from loguru import logger

from fastauth.models.schemas import (
    LoginUserRequest,
    LoginUserResponse,
    RegisterUserRequest,
    RegisterUserResponse,
)
from fastauth.models.user import FastUser
from fastauth.services import AuthenticationService
from fastauth.types import EventType


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

    def register_event(
        self,
        event: EventType,
        handler: Callable[..., Coroutine[None, None, None]],
    ) -> None:
        """
        Register a event handler. Only one event handler can be registered per event
        for now.

        Parameters
        ----------
        event : EventType
            The event to register the handler for.
        handler : Callable[..., Coroutine[None, None, None]]
            The handler to register.
        """

        self.service.events[event] = handler

    def register(self, app: FastAPI) -> None:
        self._register_routers()
        app.include_router(self.router)

    def _register_routers(self) -> None:

        @self.router.post("/register")
        async def register(body: RegisterUserRequest) -> RegisterUserResponse:

            user = await self.service.register_user(
                **body.model_dump(),
            )

            return RegisterUserResponse(user=user)

        @self.router.post("/login")
        async def login(body: LoginUserRequest) -> LoginUserResponse:

            user = await self.service.login_user(
                **body.model_dump(),
            )

            return LoginUserResponse(user=user, access_token=user.access_token)

        logger.info(f"Registered routers for FastAuth at '{self.router.prefix}'")
