from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from fastapi_users import FastAPIUsers
from models.models import User
from src.auth.manager import get_user_manager
from config import SECRET_KEY


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)

cookie_transport = CookieTransport(cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

# Зависимость: ПУСКАЕТ ТОЛЬКО ЗАЛОГИНЕННЫХ
current_active_user = fastapi_users.current_user(active=True)
# Зависимость: ПУСКАЕТ ВСЕХ, но если юзер залогинен, мы его узнаем
current_optional_user = fastapi_users.current_user(active=True, optional=True)

current_superuser = fastapi_users.current_user(active=True, superuser=True)