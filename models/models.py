from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from datetime import datetime, timezone, timedelta
from database import Base
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # ВСЕ ЭТИ ПОЛЯ ДОБАВЯТСЯ АВТОМАТИЧЕСКИ ИЗ SQLAlchemyBaseUserTable:
    # email: str (unique, index)
    # hashed_password: str
    # is_active: bool (по умолчанию True)
    # is_superuser: bool (по умолчанию False)
    # is_verified: bool (по умолчанию False)
    username = Column(String, nullable=True)


class Link(Base):
    __tablename__ = "link"
    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    last_used_at = Column(TIMESTAMP, nullable=True, index=True)
    click_count = Column(Integer, default=0) # сколько раз вызывали метод redirect
    expires_at = Column(TIMESTAMP, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class Link_click(Base):
    __tablename__ = "link_clicks"
    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("link.id"), nullable=False)
    date = Column(TIMESTAMP, default=datetime.now)
    client_ip = Column(Integer, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    referrer = Column(String, nullable=True) # ресурс откуда был клик
    device = Column(String, nullable=True) # предпологаемый девайс пользователя Mobile или Desktop, Tablet


