from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class AIModelCreate(BaseModel):
    name: str
    provider: str
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = True


class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = None


class AIModelResponse(BaseModel):
    id: UUID
    name: str
    provider: str
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
