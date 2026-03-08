import secrets
import string
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from .database_service import get_by_code, create_link, update_link
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

async def create_custom_link(db: AsyncSession, url: str, alias: str):
        existing = await get_by_code(db, short_code=alias)
        if existing is None:
            await create_link(db, original_url=url, short_code=alias)
            return True
        else: return False


async def set_livetime(db: AsyncSession, alias: str, expire_at: datetime):
      link = await get_by_code(db, short_code=alias)
      if not link:
         raise HTTPException(status_code=404, detail="Short link not found")
      
      link.expires_at = expire_at.replace(tzinfo=None)
      await db.commit()
      return True