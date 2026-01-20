from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProjectCollaboratorBase(BaseModel):
    user_id: UUID
    role: str  # owner, editor, viewer


class ProjectCollaboratorCreate(ProjectCollaboratorBase):
    pass


class ProjectCollaboratorRead(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
