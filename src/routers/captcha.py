import uuid
from io import BytesIO
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fast_captcha import img_captcha
import redis
from config import REDIS_URL

router = APIRouter(prefix="/captcha", tags=["captcha"])

redis_client = redis.asyncio.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)

CAPTCHA_TTL = 300  # 5 минут


@router.get("", summary="Получить капчу")
async def get_captcha():
    # img - bytes, text - строка
    img, text = img_captcha()
    captcha_id = str(uuid.uuid4())

    await redis_client.setex(f"captcha:{captcha_id}", CAPTCHA_TTL, text.lower())

    headers = {"X-Captcha-Id": captcha_id}
    return StreamingResponse(
        content=img,                  # уже bytes
        media_type="image/jpeg",
        headers=headers,
    )
