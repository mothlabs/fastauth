# FastAuth

FastAuth is a lightning fast in-house FastAPI authentication library that simplifies the process of handling user authentication. FastAuth uses beanie under the hood to store user credentials and redis to cache access tokens.

## Stack

In order to use FastAuth, your software/web application must follow the following stack:

- FastAPI as the API layer
- MongoDB + Beanie as the ODM library
- Redis + Redis OM

## Setup

Setting up FastAuth is simple and straightforward. When you first create your app.py, it is important that you initialize beanie and the proper documents.

```py
@asynccontextmanager
async def lifespan(_):
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client.fastauth_example, document_models=[User])

    logger.info("Connected to MongoDB and initialized documents.")

    yield

app = FastAPI(lifespan=lifespan)
```

The `User` model in this case is a custom user model that inherits from `FastUser`.

```py
class Profile(BaseModel):
    name: str | None = None
    bio: str | None = None
    birthdate: dt.datetime | None = None


class User(FastUser):
    profile: Profile = Field(default_factory=Profile)

    class Settings:
        name = "users"
```

As you can see, you don't necessarily have to use FastUser as your user model. You can extend it to your likings.

After initializing the necessary documents, simply init the FastAuth class and pass your user model in like so.

```py
auth = FastAuth(user_model=User)
auth.register(app=app)
```

And that's it! The necessary endpoints will now be accessible via the `/auth` prefix.

Now what about caching? Simple, just ensure that you have your `REDIS_OM_URL` environmental variable pointing at the correct Redis URL. Caching is done automatically at this point.

### Authenticated Endpoints

The implementation of authenticated endpoints is entirely up to you. But to make it easier, FastAuth exposes a `is_authenticated` coroutine under `auth.service`.

Here's a example of how you would make a authenticated endpoint.

```py
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

@app.get("/authenticated-route")
async def authenticated_route(is_authenticated: IsAuthenticatedDependency):
    return {"is_authenticated": is_authenticated}
```

This approaches assumes that the client passes the user id and access token via the `X-User-Id` and `X-Access-Token` headers.
