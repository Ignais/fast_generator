from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from generator_app.app.core.database import get_db
from generator_app.app.core.security import get_current_user
from generator_app.app.core.security import requires_permission

from generator_app.app.services.auth_service import AuthService
from generator_app.app.services.user_service import UserService

from generator_app.app.schemas.user import UserCreate, UserLogin, UserRead, Token
from generator_app.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
@requires_permission("user:create")
async def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.register(payload, db)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    token = await AuthService.login(payload, db)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return await UserService.get_me(current_user)


