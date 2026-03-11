import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException
from src.services.database_service import get_user_db
from models.models import User
from config import RESET_PASSWORD_SECRET
from src.auth.email import send_email 

FRONTEND_RESET_URL = "https://scraftil.ru/reset-password"

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = RESET_PASSWORD_SECRET
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
    
    async def validate_password(
        self,
        password: str,
        user: User,
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
    
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        reset_link = f"{FRONTEND_RESET_URL}?token={token}"
        send_email(
            to=user.email,
            subject="Восстановление пароля",
            body=f"Перейдите по ссылке для смены пароля: {reset_link}",
        )

    async def on_after_reset_password(
        self, user: User, request: Optional[Request] = None
    ):
        pass #оставил на будущее, если захочу отправлять письмо после смены пароля.


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
