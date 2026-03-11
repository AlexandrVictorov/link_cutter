from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from src.auth.auth import fastapi_users
from models.models import User
from models.schemas import UserRead, UserCreate, CaptchaMixin
from src.services.custom_service import verify_captcha

router = APIRouter(prefix="/auth", tags=["auth"])

UserManagerDep = fastapi_users.get_user_manager

class UserCreateWithCaptcha(UserCreate, CaptchaMixin):
    pass

@router.post("/register", response_model=UserRead)
async def register(
    user_create: UserCreateWithCaptcha,
    user_manager=Depends(UserManagerDep),
):
    await verify_captcha(user_create.captcha_id, user_create.captcha_answer)
    data = user_create.model_dump(exclude={"captcha_id", "captcha_answer"})
    return await user_manager.create(UserCreate(**data), safe=True)
