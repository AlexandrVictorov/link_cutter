# методы работы с базой данных
from sqlalchemy import select, delete
from models.models import Link, User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from database import redis_cache, get_db
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi import Depends, HTTPException


async def get_by_code(db: AsyncSession, short_code: str) -> Link | None:
    stmt = select(Link).filter(Link.short_code == short_code)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_link(db: AsyncSession, original_url: str, short_code: str, user_id: int) -> Link:
    link = Link(original_url=original_url, short_code=short_code, user_id=user_id)
    db.add(link)  #это локальная операция, await не нужен
    await db.commit()
    await db.refresh(link)
    return link


async def delete_link(db: AsyncSession, short_code: str, user) -> bool:
    link = await get_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own links")
    
    await db.delete(link)
    await db.commit()
    return True


async def update_link(db: AsyncSession, short_code: str, new_short_code: str) -> Link | None:
    link = await get_by_code(db, short_code)
    if not link:
        return None
    
    link.short_code = new_short_code
    link.created_at = datetime.now #не сказано, но думаю обновление ссылки - это по сути новая ссылка, поэтому переопределяю дату создания и обнуляю счетчик
    link.click_count = 0

    await db.commit()
    await db.refresh(link)
    return link


async def search_by_url(db: AsyncSession, url: str, user):
    user_id = user.id
    stmt = select(Link).filter(Link.original_url == url, Link.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_expired_links(db: AsyncSession):
    now = datetime.now()
    stmt = delete(Link).where(Link.expires_at != None, Link.expires_at <= now)
    result = await db.execute(stmt)
    await db.commit()
    
    #возвращаем сколько строк удалили
    return result.rowcount


async def cleanup_inactive_links(db_session: AsyncSession):
    n_days_str = await redis_cache.get("global_inactive_days")
    count = 0
    if n_days_str:
       n_days = int(n_days_str)
       cutoff_date = datetime.now() - timedelta(days=n_days)
       stmt = delete(Link).where(Link.last_used_at < cutoff_date)
       result = await db_session.execute(stmt)
       await db_session.commit()
       count = result.rowcount
    return count

#методы для работы с Users
async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)