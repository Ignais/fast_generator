from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any


# -----------------------------
# Base
# -----------------------------
class ProjectBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    definition_json: Any
    is_public: bool = False


# -----------------------------
# Create
# -----------------------------
class ProjectCreate(ProjectBase):
    pass


# -----------------------------
# Update
# -----------------------------
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    definition_json: Optional[Any] = None
    is_public: Optional[bool] = None


# -----------------------------
# Read
# -----------------------------
class ProjectRead(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    slug: str
    description: Optional[str]
    definition_json: Any
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# -----------------------------
# Read (list)
# -----------------------------
class ProjectListItem(BaseModel):
    id: UUID
    name: str
    slug: str
    is_public: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
