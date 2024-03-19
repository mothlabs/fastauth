from fastapi import HTTPException
from starlette import status


class UserAlreadyExists(HTTPException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with the email '{email}' already exists.",
        )
