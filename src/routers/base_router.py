from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.base_service import create_short_link, redirect_to_origin, put_new_link, get_statistic
from ..services.database_service import delete_link
from ..services.custom_service import create_custom_link, set_livetime
from models.schemas import LinkCreateRequest
from database import get_db

"""
Создание / удаление / изменение / получение информации по короткой ссылке:
POST /links/shorten – создает короткую ссылку или кастомную ссылку, если указан параметр alias
GET /links/{short_code} – перенаправляет на оригинальный URL.
DELETE /links/{short_code} – удаляет связь.
PUT /links/{short_code} – обновляет URL
GET /links/{short_code}/stats - Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использовани

"""

router = APIRouter(prefix="/base")

@router.post("/links/shorten")
async def create(request: LinkCreateRequest, db: AsyncSession = Depends(get_db)):
    url = str(request.original_url)
    alias = request.alias

    if not alias:
        length = getattr(request, 'length', 6) 
        result = await create_short_link(db, url, length)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create link")
            
        return {"short_link": f"http://127.0.0.1:8000/base/links/{result}"}
        
    else:
        result = await create_custom_link(db, url, alias)
        if not result:
            raise HTTPException(status_code=400, detail="This alias is already taken")
            
        return {"short_link": f"http://127.0.0.1:8000/base/links/{alias}"}

    
@router.get("/links/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_db)):
    return await redirect_to_origin(db, short_code)


@router.delete("/links/{short_code}")
async def delete(short_code: str, db: AsyncSession = Depends(get_db)):
    return await delete_link(db, short_code)


@router.put("/links/{short_code}")
async def put(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await put_new_link(db, short_code)
    if not result: return {"Error"}
    return {"short_link": result}

@router.get("/links/{short_code}/stats")
async def stat(short_code: str, db: AsyncSession = Depends(get_db)):
    return await get_statistic(db, short_code)
