import uuid
from typing import Optional
from fastapi import Request, Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.models.models import User
from app.api.dependencies import get_user_db
import secrets

SECRET = str(secrets.token_urlsafe(32))

# UserManager class to handle user-related operations
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    # Override the on_after_register method to perform actions after user registration
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    # Override the on_after_forgot_password method to perform actions after a user requests a password reset
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    # Override the on_after_request_verify method to perform actions after a user requests email verification
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

# Async generator function to provide a user manager instance
async def get_user_manager(user_db : SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# Define the authentication backend using JWT strategy
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Function to get the JWT strategy for authentication
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# Define the authentication backend using the Bearer transport and JWT strategy
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)

# Create an instance of FastAPIUsers with the User model and UUID type
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)