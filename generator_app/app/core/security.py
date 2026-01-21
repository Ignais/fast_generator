from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from generator_app.app.core.logging_config import logger
from generator_app.app.core.config import settings
from generator_app.app.core.database import get_db
from generator_app.app.models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def get_current_user( credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db) ):
    token = credentials.credentials
    logger.debug(f"Token recibido: {token}")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError as e:
        logger.warning(f"Token inválido: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        logger.warning(f"Usuario no encontrado para token: {user_id}")
        raise HTTPException(status_code=401, detail="User not found")

    return user

def requires_permission(permission_code: str):
    def decorator(func):
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db),
            **kwargs
        ):
            role = current_user.role

            if not role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned"
                )

            permission_codes = {p.code for p in role.permissions}

            if permission_code not in permission_codes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permission: {permission_code}"
                )

            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper
    return decorator
