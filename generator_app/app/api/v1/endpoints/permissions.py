from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from generator_app.app.core.database import get_db
from generator_app.app.schemas.permission import (
    PermissionCreate, PermissionUpdate, PermissionResponse
)
from generator_app.app.models.permission import Permission

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/", response_model=PermissionResponse)
def create_permission(payload: PermissionCreate, db: Session = Depends(get_db)):
    perm = Permission(code=payload.code, description=payload.description)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.get("/", response_model=list[PermissionResponse])
def list_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).all()


@router.put("/{perm_id}", response_model=PermissionResponse)
def update_permission(perm_id: str, payload: PermissionUpdate, db: Session = Depends(get_db)):
    perm = db.query(Permission).filter(Permission.id == perm_id).first()
    if not perm:
        raise HTTPException(404, "Permission not found")

    perm.code = payload.code
    perm.description = payload.description

    db.commit()
    db.refresh(perm)
    return perm


@router.delete("/{perm_id}")
def delete_permission(perm_id: str, db: Session = Depends(get_db)):
    perm = db.query(Permission).filter(Permission.id == perm_id).first()
    if not perm:
        raise HTTPException(404, "Permission not found")

    db.delete(perm)
    db.commit()
    return {"message": "Permission deleted"}
