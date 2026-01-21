from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from generator_app.app.models.user import User
from generator_app.app.core.security import verify_password, create_access_token

import logging
logger = logging.getLogger("fastapi_app")


class AuthService:

    @staticmethod
    async def login(payload, db: Session):
        logger.info(f"Intento de login para email: {payload.email}")

        user = await run_in_threadpool(
            lambda: db.query(User).filter(User.email == payload.email).first()
        )

        if not user:
            logger.warning(f"Login fallido: usuario no encontrado ({payload.email})")
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not verify_password(payload.password, user.password_hash):
            logger.warning(f"Login fallido: contraseña incorrecta ({payload.email})")
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({"sub": str(user.id)})
        logger.info(f"Login exitoso para usuario ID={user.id}")

        return token
