import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import AsyncSessionLocal
from src.routers.base_router import router as base
from src.routers.new_router import router as custom
from src.services.database_service import delete_expired_links
import logging

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

app.include_router(base)
app.include_router(custom)


@app.get("/")
async def hello():
    return {"linc_cutter запущен!"}
