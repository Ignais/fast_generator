from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Any


class ProjectVersionRead(BaseModel):
    id: UUID
    project_id: UUID
    version: int
    definition_json: Any
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
