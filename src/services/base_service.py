import secrets
import string
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from .database_service import get_by_code, create_link, update_link
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

ALPHABET = string.ascii_letters + string.digits

async def create_short_link(db: AsyncSession, url: str, length: int = 6) -> str: # функция генерации короткой ссылки устуновленной длины
    while True:
        short_code = ''.join(secrets.choice(ALPHABET) for _ in range(length))
        existing = await get_by_code(db, short_code=short_code)
        if existing is None:
            await create_link(db, original_url=url, short_code=short_code)
            return short_code


async def redirect_to_origin(db: AsyncSession, short_url: str):
    link = await get_by_code(db, short_code=short_url)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    link.click_count += 1 #увеличиваю счетчик переходов
    link.last_used_at = datetime.now() 
    await db.commit()

    return RedirectResponse(
        url=link.original_url,
        status_code=307
    )


async def put_new_link(db: AsyncSession, short_url: str):
    while True:
        short_code = ''.join(secrets.choice(ALPHABET) for _ in range(len(short_url)))
        existing = await get_by_code(db, short_code=short_code)
        if existing is None:
            await update_link(db, short_code=short_url, new_short_code=short_code)
            return short_code
        

async def get_statistic(db: AsyncSession, short_url: str):
    link = await get_by_code(db, short_code=short_url)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    return {'Original_URL': link.original_url,
            'Created': link.created_at,
            'Clicks': link.click_count,
            'Last_click': link.last_used_at,
             }

