from pydantic import BaseModel
from typing import Any

class AIGenerateRequest(BaseModel):
    prompt: str

class AIGenerateResponse(BaseModel):
    definition_json: Any
