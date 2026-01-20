from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None

    model_config = {
        "from_attributes": True
    }
