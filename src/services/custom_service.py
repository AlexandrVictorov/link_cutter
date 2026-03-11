import secrets
import string
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from .database_service import get_by_code, create_link, update_link
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from src.routers.captcha import redis_client

async def create_custom_link(db: AsyncSession, url: str, alias: str, user_id):
        
        existing = await get_by_code(db, short_code=alias)
        if existing is None:
            await create_link(db, original_url=url, short_code=alias, user_id=user_id)
            return True
        else: return False


async def set_livetime(db: AsyncSession, alias: str, expire_at: datetime, user):
      link = await get_by_code(db, short_code=alias)
      if not link:
         raise HTTPException(status_code=404, detail="Short link not found")
      
      if link.user_id is None or link.user_id != user.id:
         raise HTTPException(status_code=403, detail="Вы не можете редактировать чужую ссылку")

      link.expires_at = expire_at.replace(tzinfo=None)
      await db.commit()
      return True


async def verify_captcha(captcha_id: str, answer: str):
    key = f"captcha:{captcha_id}"
    real = await redis_client.get(key)
    if not real:
        raise HTTPException(status_code=400, detail="Captcha expired")
    await redis_client.delete(key)
    if real != answer.lower():
        raise HTTPException(status_code=400, detail="Wrong captcha")