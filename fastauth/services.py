from fastauth.models.user import FastUser


class AuthenticationService:
    def __init__(self, user_model: FastUser) -> None:
        self.user_model = user_model
