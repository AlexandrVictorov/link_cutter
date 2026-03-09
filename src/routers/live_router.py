from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.custom_service import set_livetime
from ..services.database_service import search_by_url
from models.schemas import DeadLink
from database import get_db, redis_cache
from models.models import User
from src.auth.auth import current_superuser, current_active_user, current_optional_user
"""
4. Поиск ссылки по оригинальному URL:
  - `GET /links/search?original_url={url}`
5. Указание времени жизни ссылки:
  - `POST /links/shorten` (создается с параметром `expires_at` в формате даты с точностью до минуты).
  - После указанного времени короткая ссылка автоматически удаляется.
6. Удаление неиспользуемых ссылок через N дней после крайнего использования.
"""

router = APIRouter(prefix="/live")

@router.get("/links/search")
async def search(original_url: str, db: AsyncSession = Depends(get_db), user: User = Depends(current_optional_user)):
    links = await search_by_url(db, original_url, user)
    if not links:
        raise HTTPException(status_code=404, detail="Short links not found for this URL")
    
    short_codes = [link.short_code for link in links]
    
    return {
        "original_url": original_url,
        "aliases": short_codes
    }


@router.post("/links/shorten/set_n/{n}")
async def set_n(n: int = 30, db: AsyncSession = Depends(get_db), user: User = Depends(current_superuser)):
    await redis_cache.set("global_inactive_days", n)
    return {"status": f"Удаление неактивных ссылок установлено через {n} дней"}


@router.post("/links/shorten")
async def livetime(request: DeadLink, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    alias = request.alias
    expire_at = request.expires_at
    return await set_livetime(db, alias, expire_at, user)


