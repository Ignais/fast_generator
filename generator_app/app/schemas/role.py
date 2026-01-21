from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class PermissionBase(BaseModel):
    id: UUID
    code: str
    description: Optional[str]

    model_config = {
        "from_attributes": True
    }


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False


class RoleCreate(RoleBase):
    permissions: List[UUID]


class RoleUpdate(RoleBase):
    permissions: List[UUID]


class RoleResponse(RoleBase):
    id: UUID
    permissions: List[PermissionBase]

    model_config = {
        "from_attributes": True
    }
