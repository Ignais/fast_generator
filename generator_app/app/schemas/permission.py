from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: UUID

    class Config:
        orm_mode = True
