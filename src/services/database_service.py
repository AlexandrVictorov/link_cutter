# методы работы с базой данных
from sqlalchemy import select, delete
from models.models import Link
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


async def get_by_code(db: AsyncSession, short_code: str) -> Link | None:
    stmt = select(Link).filter(Link.short_code == short_code)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_link(db: AsyncSession, original_url: str, short_code: str) -> Link:
    link = Link(original_url=original_url, short_code=short_code)
    db.add(link)  #это локальная операция, await не нужен
    await db.commit()
    await db.refresh(link)
    return link


async def delete_link(db: AsyncSession, short_code: str) -> bool:
    link = await get_by_code(db, short_code)
    if not link:
        return False
    
    await db.delete(link)
    await db.commit()
    return True


async def update_link(db: AsyncSession, short_code: str, new_short_code: str) -> Link | None:
    link = await get_by_code(db, short_code)
    if not link:
        return None
        
    link.short_code = new_short_code
    link.created_at = datetime.now #не сказано, но думаю обновление ссылки - это по сути новая ссылка, поэтомуо переопределяю дату создания и обнуляю счетчик
    link.click_count = 0

    await db.commit()
    await db.refresh(link)
    return link


async def search_by_url(db: AsyncSession, url: str):
    stmt = select(Link).filter(Link.original_url == url)
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_expired_links(db: AsyncSession):
    now = datetime.now()
    stmt = delete(Link).where(Link.expires_at != None, Link.expires_at <= now)
    result = await db.execute(stmt)
    await db.commit()
    
    #возвращаем сколько строк удалили
    return result.rowcount