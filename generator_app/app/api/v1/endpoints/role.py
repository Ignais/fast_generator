from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from generator_app.app.core.database import get_db
from generator_app.app.core.security import requires_permission
from generator_app.app.services.role_service import RoleService

from generator_app.app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleRead
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleRead)
@requires_permission("role:create")
async def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db)
):
    return await RoleService.create(payload, db)


@router.get("/", response_model=list[RoleRead])
@requires_permission("role:view")
async def list_roles(db: Session = Depends(get_db)):
    return await RoleService.list(db)


@router.put("/{role_id}", response_model=RoleRead)
@requires_permission("role:update")
async def update_role(
    role_id: str,
    payload: RoleUpdate,
    db: Session = Depends(get_db)
):
    return await RoleService.update(role_id, payload, db)


@router.post("/{role_id}/permissions/{permission_id}", response_model=RoleRead)
@requires_permission("role:update")
async def assign_permission_to_role(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db)
):
    return await RoleService.assign_permission(role_id, permission_id, db)
