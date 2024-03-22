from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from beanie import init_beanie
from fastapi import Depends, FastAPI, Header
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from redis_om import Migrator

from fastauth import FastAuth

from .models import User

MONGODB_URI = "mongodb://matt:admin@localhost:27017/"


# Setting up beanie and the database
@asynccontextmanager
async def lifespan(_):
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client.fastauth_example, document_models=[User])

    logger.info("Connected to MongoDB and initialized documents.")

    Migrator().run()

    logger.info("Migrated redis documents.")

    yield


# Setting up FastAuth
app = FastAPI(lifespan=lifespan)
auth = FastAuth(user_model=User)
auth.register(app=app)


async def is_authenticated(
    x_user_id: Annotated[str | None, Header()] = None,
    x_access_token: Annotated[str | None, Header()] = None,
) -> bool:

    if x_user_id is None or x_access_token is None:
        return False

    return await auth.service.is_authenticated(
        user_id=x_user_id, access_token=x_access_token
    )


IsAuthenticatedDependency = Annotated[bool, Depends(is_authenticated)]


# A example of events
@auth.on("on_register")
async def on_register(user: User):
    logger.info(
        f"on_register event triggered. Registered user with email '{user.email}'."
    )


@app.get("/")
async def index():
    return {"message": "Welcome to FastAuth!"}


@app.get("/authenticated-route")
async def authenticated_route(is_authenticated: IsAuthenticatedDependency):
    return {"is_authenticated": is_authenticated}


def main():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )


if __name__ == "__main__":
    main()
