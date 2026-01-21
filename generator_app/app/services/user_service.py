from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from generator_app.app.models.user import User
from generator_app.app.models.role import Role
from generator_app.app.core.security import hash_password

import logging
logger = logging.getLogger("fastapi_app")


class UserService:

    @staticmethod
    async def register(payload, db: Session):
        logger.warning(f"PAYLOAD RECIBIDO: {payload}")

        if len(payload.password.encode("utf-8")) > 72:
            raise HTTPException(status_code=400, detail="Password too long")

        # Verificar si existe
        existing = await run_in_threadpool(
            lambda: db.query(User).filter(User.email == payload.email).first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Rol opcional
        role = None
        if payload.role_id:
            role = await run_in_threadpool(
                lambda: db.query(Role).filter(Role.id == payload.role_id).first()
            )
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")

        hashed = hash_password(payload.password)

        def create_user():
            user = User(
                email=payload.email,
                full_name=payload.full_name,
                password_hash=hashed,
                role_id=payload.role_id if role else None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        user = await run_in_threadpool(create_user)
        logger.warning(f"USUARIO CREADO: {user.id}")

        return user

    @staticmethod
    async def get_me(current_user: User):
        return current_user
