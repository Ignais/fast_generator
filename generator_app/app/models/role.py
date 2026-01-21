from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from generator_app.app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    is_default = Column(Boolean, default=False)

    # relación con permisos
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )

    # relación con usuarios
    users = relationship("User", back_populates="role")
