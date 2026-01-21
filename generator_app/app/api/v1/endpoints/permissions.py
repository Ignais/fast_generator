from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from generator_app.app.core.database import get_db
from generator_app.app.core.security import requires_permission
from generator_app.app.services.permission_service import PermissionService

from generator_app.app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionRead
)

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/", response_model=PermissionRead)
@requires_permission("permission:create")
async def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db)
):
    return await PermissionService.create(payload, db)


@router.get("/", response_model=list[PermissionRead])
@requires_permission("permission:view")
async def list_permissions(db: Session = Depends(get_db)):
    return await PermissionService.list(db)


@router.put("/{permission_id}", response_model=PermissionRead)
@requires_permission("permission:update")
async def update_permission(
    permission_id: str,
    payload: PermissionUpdate,
    db: Session = Depends(get_db)
):
    return await PermissionService.update(permission_id, payload, db)


@router.delete("/{permission_id}")
@requires_permission("permission:delete")
async def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db)
):
    return await PermissionService.delete(permission_id, db)
