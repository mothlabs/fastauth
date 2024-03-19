# FastAuth

FastAuth is a lightning fast in-house FastAPI authentication library that simplifies the process of handling user authentication. FastAuth uses beanie under the hood to store user credentials and redis to cache access tokens.

## Stack

In order to use FastAuth, your software/web application must follow the following stack:

- FastAPI as the API layer
- MongoDB + Beanie as the ODM library
- Redis
