# методы работы с базой данных
from sqlalchemy import select, delete, func
from models.models import Link, User, Link_click
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from datetime import date as DateType
from typing import Any
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


async def get_daily_click_stats(db: AsyncSession, link_id: int, day: DateType,) -> dict[str, Any]:
    """
    Статистика по кликам для одной ссылки за конкретный день.
    day - объект datetime.date
    """

    # date(Link_click.date) == day  (Postgres/SQLite/и т.п.) [web:35][web:50]
    base_filter = (
        (Link_click.link_id == link_id) &
        (func.date(Link_click.date) == day)
    )

    # 1) Страны
    stmt_countries = (
        select(
            Link_click.country,
            func.count().label("clicks"),
        )
        .where(base_filter)
        .group_by(Link_click.country)
        .order_by(func.count().desc())
    )
    res_countries = (await db.execute(stmt_countries)).all()
    by_country = [
        {"country": country or "Unknown", "clicks": clicks}
        for country, clicks in res_countries
    ]

    # 2) Города
    stmt_cities = (
        select(
            Link_click.city,
            func.count().label("clicks"),
        )
        .where(base_filter)
        .group_by(Link_click.city)
        .order_by(func.count().desc())
    )
    res_cities = (await db.execute(stmt_cities)).all()
    by_city = [
        {"city": city or "Unknown", "clicks": clicks}
        for city, clicks in res_cities
    ]

    # 3) Устройства
    stmt_devices = (
        select(
            Link_click.device,
            func.count().label("clicks"),
        )
        .where(base_filter)
        .group_by(Link_click.device)
        .order_by(func.count().desc())
    )
    res_devices = (await db.execute(stmt_devices)).all()
    by_device = [
        {"device": device or "Unknown", "clicks": clicks}
        for device, clicks in res_devices
    ]

    # 4) Источники (referrer)
    stmt_referrers = (
        select(
            Link_click.referrer,
            func.count().label("clicks"),
        )
        .where(base_filter)
        .group_by(Link_click.referrer)
        .order_by(func.count().desc())
    )
    res_referrers = (await db.execute(stmt_referrers)).all()
    referrers = [
        {"referrer": ref or "Direct / None", "clicks": clicks}
        for ref, clicks in res_referrers
    ]

    return {
        "by_country": by_country,
        "by_city": by_city,
        "by_device": by_device,
        "referrers": referrers,
    }


async def get_clicks_by_day(db: AsyncSession, link_id: int):
    
    #Возвращает список словарей День - число кликов за последние 30 дей.
    
    today = datetime.now(timezone.utc).date()
    from_date = today - timedelta(days=30)

    stmt = (
        select(
            func.date(Link_click.date).label("day"),
            func.count().label("clicks"),
        )
        .where(
            Link_click.link_id == link_id,
            func.date(Link_click.date) >= from_date,
            func.date(Link_click.date) <= today,
        )
        .group_by(func.date(Link_click.date))
        .order_by(func.date(Link_click.date))
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [{"date": day, "clicks": clicks} for day, clicks in rows]