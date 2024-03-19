import secrets
from typing import Type

import bcrypt

from fastauth.exceptions import UserAlreadyExists
from fastauth.models.user import FastUser


class AuthenticationService:
    def __init__(self, user_model: Type[FastUser]) -> None:
        self.user_model = user_model

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

        return user
