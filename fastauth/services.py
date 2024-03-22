import secrets
from typing import Callable, Coroutine, Type

import bcrypt
from loguru import logger

from fastauth.exceptions import Unauthenticated, UserAlreadyExists
from fastauth.models.user import FastUser
from fastauth.types import EventType


class AuthenticationService:
    def __init__(self, user_model: Type[FastUser]) -> None:
        self.user_model = user_model
        self.events: dict[EventType, Callable[..., Coroutine[None, None, None]]] = {}

    def generate_access_token(self) -> str:
        """
        Generate a brand new, 24 character access token.

        Returns
        -------
        str
            The access token.
        """

        return secrets.token_hex(24)

    async def register_user(self, email: str, password: str) -> FastUser:
        """
        Register a new user.

        Events
        ------
        on_register : Callable[[FastUser], Coroutine[None, None, None]]
            Called when a new user is registered. The user is passed as a parameter.

        Parameters
        ----------
        email : str
            The email of the user.
        password : str
            The password of the user.

        Returns
        -------
        FastUser
            The created user.
        """

        if await self.user_model.find_one(self.user_model.email == email):
            raise UserAlreadyExists(email)

        encrypted_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        access_token = self.generate_access_token()

        user = self.user_model(
            email=email,
            password=encrypted_password,
            access_token=access_token,
        )
        await user.save()

        logger.info(f"Registered user with email '{email}'.")

        if "on_register" in self.events:
            await self.events["on_register"](user)

        return user

    async def login_user(self, email: str, password: str) -> FastUser:
        """
        Login a user.

        Events
        ------
        on_login : Callable[[FastUser], Coroutine[None, None, None]]
            Called when a user is logged in. The user is passed as a parameter.

        Parameters
        ----------
        email : str
            The email of the user.
        password : str
            The password of the user.

        Returns
        -------
        FastUser
            The logged in user.
        """

        user = await self.user_model.find_one(self.user_model.email == email)
        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user.password):
                user.authenticated = True
                await user.save()

                logger.info(f"Logged in user with email '{email}'.")

                if "on_login" in self.events:
                    await self.events["on_login"](user)

                return user

        raise Unauthenticated
