from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional

class FieldDefinition(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    unique: bool = False

class RelationshipDefinition(BaseModel):
    name: str
    type: str
    model: str

class ModelDefinition(BaseModel):
    name: str
    fields: List[FieldDefinition] = Field(default_factory=list)
    relationships: List[RelationshipDefinition] = Field(default_factory=list)

class ProjectDefinition(BaseModel):
    project_name: str
    version: str = "1.0.0"
    description: str = "Generated FastAPI project"
    mode: str = "api"
    backend: str = "fastapi"
    frontend: str = "none"
    dependencies: List[str] = Field(default_factory=lambda: ["fastapi", "uvicorn"])
    routes: List[Dict[str, Any]] = Field(default_factory=list)
    env: Dict[str, Any] = Field(default_factory=dict)
    database: str = "sqlite"

    @field_validator("database", mode="before")
    @classmethod
    def ensure_database(cls, v):
        return v or "sqlite"

class NormalizedDefinition(BaseModel):
    project: ProjectDefinition
    models: List[ModelDefinition] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
