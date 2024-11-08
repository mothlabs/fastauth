import datetime as dt
import secrets
from typing import Callable, Coroutine, Type

import bcrypt
from loguru import logger
from redis import ResponseError
from redis_om import NotFoundError

from fastauth.exceptions import Unauthenticated, UserAlreadyExists, UserNotFound
from fastauth.models.user import CachedUser, FastUser
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

    def recache(
        self, user_id: str, access_token: str, authenticated: bool = False
    ) -> CachedUser:
        """
        Recache a user's access token.

        Parameters
        ----------
        user_id : str
            The ID of the user.
        access_token : str
            The access token.
        authenticated : bool
            Whether the user is authenticated.
        """

        try:
            cache: CachedUser = CachedUser.find(CachedUser.id == user_id).first()
            cache.access_token = access_token
            cache.authenticated = 1 if authenticated else 0
        except NotFoundError:
            cache = CachedUser(
                id=user_id,
                access_token=access_token,
                authenticated=1 if authenticated else 0,
            )

        cache.save()
        cache.expire(600)

        logger.debug(f"Recached user with ID '{user_id}'. Primary key is '{cache.pk}'.")

        return cache

    async def is_authenticated(self, user_id: str, access_token: str) -> bool:
        """
        Check if the provided user and its access token is authenticated.
        """

        try:
            cache: CachedUser | None = CachedUser.find(
                CachedUser.id == user_id, CachedUser.access_token == access_token
            ).first()
        except (NotFoundError, ResponseError):
            cache = None

        if cache is not None:
            if cache.authenticated == 1:
                return True
            return False

        user = await self.user_model.find_one(
            self.user_model.id == user_id,
            self.user_model.access_token == access_token,
        )

        authenticated = False
        if user is not None:
            authenticated = True

        self.recache(user_id, access_token, authenticated=authenticated)

        return authenticated

    async def register_user(self, email: str, password: str) -> FastUser:
        """
        Register a new user.

        Events
        ------
        on_register : Callable[[FastUser], Coroutine[None, None, None]]
            Called when a new user is registered. The user is passed as a parameter.

        Raises
        ------
        UserAlreadyExists
            If the user already exists.

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

        self.recache(user.id, access_token, authenticated=True)
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

        Raises
        ------
        Unauthenticated
            If the user is not authenticated.

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
                user.last_login = dt.datetime.now(tz=dt.timezone.utc)
                await user.save()

                self.recache(user.id, user.access_token, authenticated=True)
                logger.info(f"Logged in user with email '{email}'.")

                if "on_login" in self.events:
                    await self.events["on_login"](user)

                return user

        raise Unauthenticated

    async def delete_user(self, user_id: str) -> None:
        """
        Delete a user.

        Events
        ------
        on_delete : Callable[[FastUser], Coroutine[None, None, None]]
            Called when a user is deleted. The user is passed as a parameter.

        Raises
        ------
        UserNotFound
            If the user is not found.

        Parameters
        ----------
        user_id : str
            The ID of the user.
        """

        user = await self.user_model.find_one(self.user_model.id == user_id)
        if user is None:
            raise UserNotFound(detail={"user_id": user_id})

        await user.delete()

        logger.info(f"Deleted user with ID '{user_id}'.")
        if "on_delete" in self.events:
            await self.events["on_delete"](user)

        self.recache(user.id, user.access_token, authenticated=False)
