import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import AsyncSessionLocal
from src.routers.base_router import router as base
from src.routers.live_router import router as live
from src.services.database_service import delete_expired_links, cleanup_inactive_links
import logging
from src.auth.auth import fastapi_users, auth_backend
from models.schemas import UserRead, UserCreate
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.routers.captcha import router as captcha 
from src.routers.auth_router import router as auth_router

logger = logging.getLogger(__name__)

# Эта функция будет крутиться в фоне бесконечно
async def cleanup_task():
    while True:
        try:
            #новая сессия
            async with AsyncSessionLocal() as session:
                deleted_count = await delete_expired_links(session)
                if deleted_count > 0:
                    logger.info(f"Удалено устаревших ссылок: {deleted_count}")

                deleted_count = await cleanup_inactive_links(session)
                if deleted_count > 0:
                    logger.info(f"Удалено неактивных ссылок: {deleted_count}")

        except Exception as e:
            logger.error(f"Ошибка при удалении ссылок: {e}")
            
        await asyncio.sleep(60) #проверка каждые 60 секунд

# Привязываем фоновую задачу к жизненному циклу FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cleanup_task())
    yield
    task.cancel()


app = FastAPI(title="link_cutter", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(base)
app.include_router(live)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(auth_router)
app.include_router(captcha)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

@app.get("/")
async def frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
