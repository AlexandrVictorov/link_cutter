from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.base_service import create_short_link, redirect_to_origin, put_new_link, get_statistic, get_regions
from ..services.database_service import delete_link, get_by_code
from ..services.custom_service import create_custom_link, set_livetime
from ..services.ip_service import get_client_ip, get_geo_by_ip, get_device_type
from models.schemas import LinkCreateRequest
from models.models import User, Link_click
from src.auth.auth import current_optional_user, current_active_user
from database import get_db, redis_cache
from datetime import datetime
from datetime import date as DateType

"""
Создание / удаление / изменение / получение информации по короткой ссылке:
POST /links/shorten – создает короткую ссылку или кастомную ссылку, если указан параметр alias
GET /links/{short_code} – перенаправляет на оригинальный URL.
DELETE /links/{short_code} – удаляет связь.
PUT /links/{short_code} – обновляет URL
GET /links/{short_code}/stats - Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использовани

"""

router = APIRouter()


@router.post("/links/shorten")
async def create(request: Request, body: LinkCreateRequest, db: AsyncSession = Depends(get_db), user: User = Depends(current_optional_user)):
    url = str(body.original_url)
    alias = body.alias
    user_id = user.id

    if not alias:
        length = getattr(body, 'length', 6) 
        result = await create_short_link(db, url, length, user_id=user_id)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create link")
            
        return {"short_link": f"https://scraftil.ru/links/{result}"} 
        
    else:
        result = await create_custom_link(db, url, alias, user_id=user_id)
        if not result:
            raise HTTPException(status_code=400, detail="This alias is already taken")
            
        return {"short_link": f"https://scraftil.ru/links/{alias}"}

    
@router.get("/links/{short_code}")
async def redirect(request: Request, short_code: str, db: AsyncSession = Depends(get_db)):
    link = await get_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    try:
        link.click_count += 1
        link.last_used_at = datetime.now()

        ip = get_client_ip(request)
        geo = get_geo_by_ip(ip)
        referrer = request.headers.get("referer")
        device = get_device_type(request)

        click = Link_click(
            link_id=link.id,
            client_ip=ip,
            country=geo["country"] if geo else None,
            city=geo["city"] if geo else None,
            referrer=referrer if referrer else None,
            device=device if device else None
        )
        db.add(click)
        await db.commit()
    except Exception as e:
        await db.rollback()
        print("Click analytics error:", e)

    cached_url = await redis_cache.get(short_code)
    if cached_url:
        return RedirectResponse(cached_url, status_code=307)

    return await redirect_to_origin(db, short_code, link)

@router.delete("/links/{short_code}")
async def delete(short_code: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    return await delete_link(db, short_code, user)


@router.put("/links/{short_code}")
async def put(short_code: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    result = await put_new_link(db, short_code, user)
    if not result: 
        raise HTTPException(status_code=400, detail="Error updating link")
    return {"short_link": result}


@router.get("/links/{short_code}/stats")
async def stat(short_code: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    return await get_statistic(db, short_code, user)


@router.get("/links/{short_code}/stats/regions")
async def regions(day: DateType, short_code: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    return await get_regions(day, db, short_code, user)