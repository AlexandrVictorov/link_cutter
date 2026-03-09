from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config import DB_NAME, DB_USER, DB_PORT, DB_HOST, DB_PASS, REDIS_URL
import redis.asyncio as redis


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True) 

redis_cache = redis.from_url(REDIS_URL, decode_responses=True) # экземпляр класса для кэширования

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session