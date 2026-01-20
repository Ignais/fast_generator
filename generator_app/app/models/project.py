from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4

from generator_app.app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(String)

    definition_json = Column(JSON, nullable=False)

    is_public = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    owner = relationship("User", backref="projects")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete")
    collaborators = relationship("ProjectCollaborator", back_populates="project", cascade="all, delete")
