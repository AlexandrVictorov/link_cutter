import asyncio
from typing import AsyncGenerator
import pytest
import httpx
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy import select
from src.main import app
from database import Base, get_db, DATABASE_URL
from src.auth.auth import current_optional_user, current_active_user, current_superuser
from models.models import User
from unittest.mock import AsyncMock
import redis.asyncio as redis
 


#запускаю с другим файлом окружения ENV_FILE=.env-non-dev pytest -q
TEST_DATABASE_URL = DATABASE_URL


async def _create_test_user(db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalars().first()
    if user:
        return user

    user = User(
        email="test@example.com",
        hashed_password="not_used_here",
        is_active=True,
        is_verified=True,
        is_superuser=True,  # если нужен суперюзер
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def session_maker(engine):
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture(scope="function")
async def db_session(session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    #Эта функция будет использоваться вместо get_db в тестах
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    #для понимания 'когда кто‑то просит Depends(get_db), давай ему мою тестовую db_session, а не боевую'
    app.dependency_overrides[get_db] = _override_get_db

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Чистим переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authenticated_client(db_session: AsyncSession):
    # Эта функция будет использоваться вместо get_db в тестах
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Переопределяем зависимость в приложении
    #для понимания 'когда кто‑то просит Depends(get_db), давай ему мою тестовую db_session, а не боевую'
    app.dependency_overrides[get_db] = _override_get_db

    # создаём настоящего пользователя в тестовой БД
    user = await _create_test_user(db_session)

    async def _override_current_optional_user():
        return user

    # Пускает всех, но если юзер залогинен - мы его узнаем
    app.dependency_overrides[current_optional_user] = _override_current_optional_user

    transport = httpx.ASGITransport(app=app)

    # Создаём тестовый HTTP‑клиент поверх FastAPI-приложения
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Чистим переопределения после теста
    app.dependency_overrides.pop(current_optional_user, None)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
async def active_client(db_session: AsyncSession):
    # Эта функция будет использоваться вместо get_db в тестах
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Переопределяем зависимость в приложении
    #для понимания 'когда кто‑то просит Depends(get_db), давай ему мою тестовую db_session, а не боевую'
    app.dependency_overrides[get_db] = _override_get_db

    # создаём настоящего пользователя в тестовой БД
    user = await _create_test_user(db_session)

    async def _override_current_active_user():
        return user
    
    async def _override_current_superuser():
        return user

    # ПУСКАЕТ ТОЛЬКО ЗАЛОГИНЕННЫХ
    app.dependency_overrides[current_active_user] = _override_current_active_user
    app.dependency_overrides[current_superuser] = _override_current_superuser

    transport = httpx.ASGITransport(app=app)

    # Создаём тестовый HTTP клиент поверх FastAPI-приложения
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Чистим переопределения после теста
    app.dependency_overrides.pop(current_active_user, None)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
async def fake_redis(monkeypatch):
    # Не даём тестам ходить в настоящий Redis: подменяем redis_cache во всех модулях, где он используется
    class FakeRedis:
        async def get(self, key):
            return None

        async def set(self, key, value, ex=None):
            return True

    fake = FakeRedis()

    # 1) redis_cache, созданный в database.py
    monkeypatch.setattr("database.redis_cache", fake, raising=False)

    # 2) redis_cache, импортированный в роутере
    monkeypatch.setattr("src.routers.base_router.redis_cache", fake, raising=False)

    # 3) redis_cache, импортированный в сервисе redirect_to_origin
    monkeypatch.setattr("src.services.base_service.redis_cache", fake, raising=False)
    #редис в лайв роутере
    monkeypatch.setattr("src.routers.live_router.redis_cache", fake, raising=False)

    yield
