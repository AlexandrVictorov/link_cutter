import secrets
import string
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from .database_service import get_by_code, create_link, update_link, get_daily_click_stats, get_clicks_by_day
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from database import redis_cache

ALPHABET = string.ascii_letters + string.digits
msk = timezone(timedelta(hours=3))

async def create_short_link(db: AsyncSession, url: str, length: int = 6, user_id: int = None) -> str: # функция генерации короткой ссылки устуновленной длины
    while True:
        short_code = ''.join(secrets.choice(ALPHABET) for _ in range(length))
        existing = await get_by_code(db, short_code=short_code)
        if existing is None:
            await create_link(db, original_url=url, short_code=short_code, user_id=user_id)
            return short_code


async def redirect_to_origin(db: AsyncSession, short_url: str, link):
    #кэширую запрос на 1 час (3600 сек)
    await redis_cache.set(short_url, link.original_url, ex=3600)

    return RedirectResponse(
        url=link.original_url,
        status_code=307
    )


async def put_new_link(db: AsyncSession, short_url: str, user):
    link = await get_by_code(db, short_code=short_url)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    if link.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own links")

    while True:
        short_code = ''.join(secrets.choice(ALPHABET) for _ in range(len(short_url)))
        existing = await get_by_code(db, short_code=short_code)
        if existing is None:
            await update_link(db, short_code=short_url, new_short_code=short_code)
            return short_code
        

async def get_statistic(db: AsyncSession, short_url: str, user):
    link = await get_by_code(db, short_code=short_url)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if link.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own links")
    
    clicks_by_day = await get_clicks_by_day(db, link_id=link.id)

    return {'Original_URL': link.original_url,
            'Created': link.created_at.astimezone(msk),
            'Clicks': link.click_count,
            'Last_click': link.last_used_at.astimezone(msk),
            "Clicks_by_day": clicks_by_day,  # [{date, clicks}] для графика
             }


async def get_regions(day, db: AsyncSession, short_url: str, user):
    link = await get_by_code(db, short_code=short_url)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if link.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own links")
    
    return await get_daily_click_stats(db, link.id, day)
