from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from generator_app.app.models.permission import Permission
from generator_app.app.schemas.permission import PermissionCreate, PermissionUpdate

import logging
logger = logging.getLogger("fastapi_app")


class PermissionService:

    @staticmethod
    async def create(payload: PermissionCreate, db: Session):
        existing = await run_in_threadpool(
            lambda: db.query(Permission).filter(Permission.code == payload.code).first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Permission already exists")

        def create_perm():
            perm = Permission(code=payload.code, description=payload.description)
            db.add(perm)
            db.commit()
            db.refresh(perm)
            return perm

        perm = await run_in_threadpool(create_perm)
        logger.info(f"Permission created: {perm.code}")
        return perm

    @staticmethod
    async def update(permission_id, payload: PermissionUpdate, db: Session):
        perm = await run_in_threadpool(
            lambda: db.query(Permission).filter(Permission.id == permission_id).first()
        )

        if not perm:
            raise HTTPException(status_code=404, detail="Permission not found")

        def update_perm():
            if payload.code is not None:
                perm.code = payload.code
            if payload.description is not None:
                perm.description = payload.description

            db.commit()
            db.refresh(perm)
            return perm

        return await run_in_threadpool(update_perm)

    @staticmethod
    async def delete(permission_id, db: Session):
        perm = await run_in_threadpool(
            lambda: db.query(Permission).filter(Permission.id == permission_id).first()
        )

        if not perm:
            raise HTTPException(status_code=404, detail="Permission not found")

        def delete_perm():
            db.delete(perm)
            db.commit()

        await run_in_threadpool(delete_perm)
        return {"detail": "Permission deleted"}

    @staticmethod
    async def list(db: Session):
        return await run_in_threadpool(lambda: db.query(Permission).all())
