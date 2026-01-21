from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from generator_app.app.models.role import Role
from generator_app.app.models.permission import Permission
from generator_app.app.schemas.role import RoleCreate, RoleUpdate

import logging
logger = logging.getLogger("fastapi_app")


class RoleService:

    @staticmethod
    async def create(payload: RoleCreate, db: Session):
        existing = await run_in_threadpool(
            lambda: db.query(Role).filter(Role.name == payload.name).first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Role already exists")

        def create_role():
            role = Role(
                name=payload.name,
                description=payload.description,
                is_default=payload.is_default
            )
            db.add(role)
            db.commit()
            db.refresh(role)
            return role

        role = await run_in_threadpool(create_role)
        logger.info(f"Role created: {role.name}")
        return role

    @staticmethod
    async def update(role_id, payload: RoleUpdate, db: Session):
        role = await run_in_threadpool(
            lambda: db.query(Role).filter(Role.id == role_id).first()
        )

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        def update_role():
            if payload.name is not None:
                role.name = payload.name
            if payload.description is not None:
                role.description = payload.description
            if payload.is_default is not None:
                role.is_default = payload.is_default

            db.commit()
            db.refresh(role)
            return role

        return await run_in_threadpool(update_role)

    @staticmethod
    async def assign_permission(role_id, permission_id, db: Session):
        role = await run_in_threadpool(
            lambda: db.query(Role).filter(Role.id == role_id).first()
        )
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        perm = await run_in_threadpool(
            lambda: db.query(Permission).filter(Permission.id == permission_id).first()
        )
        if not perm:
            raise HTTPException(status_code=404, detail="Permission not found")

        def assign():
            role.permissions.append(perm)
            db.commit()
            db.refresh(role)
            return role

        return await run_in_threadpool(assign)

    @staticmethod
    async def list(db: Session):
        return await run_in_threadpool(lambda: db.query(Role).all())
