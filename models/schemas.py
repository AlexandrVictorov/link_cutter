from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional
from fastapi_users import schemas

class LinkCreateRequest(BaseModel):
    original_url: HttpUrl
    length: int = Field(default=6, ge=2, le=30)  # ge = Greater than or Equal (больше или равно); le = Less than or Equal (меньше или равно)
    alias: Optional[str] = Field(default=None, min_length=2, max_length=30)


class DeadLink(BaseModel):
    alias: str
    expires_at: datetime


class UserRead(schemas.BaseUser[int]):
    # id, email, is_active и т.д. уже есть под капотом!
    username: str
    #role_id: int


class UserCreate(schemas.BaseUserCreate):
    username: str
    #role_id: int


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
    #role_id: Optional[int] = None


class CaptchaMixin(BaseModel):
    captcha_id: str
    captcha_answer: str

