from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from generator_app.app.core.database import get_db
from generator_app.app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from generator_app.app.models.role import Role
from generator_app.app.models.permission import Permission

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleResponse)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    role = Role(
        name=payload.name,
        description=payload.description,
        is_default=payload.is_default
    )

    if payload.permissions:
        perms = db.query(Permission).filter(Permission.id.in_(payload.permissions)).all()
        role.permissions = perms

    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: str, payload: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")

    role.name = payload.name
    role.description = payload.description
    role.is_default = payload.is_default

    perms = db.query(Permission).filter(Permission.id.in_(payload.permissions)).all()
    role.permissions = perms

    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}")
def delete_role(role_id: str, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")

    db.delete(role)
    db.commit()
    return {"message": "Role deleted"}
