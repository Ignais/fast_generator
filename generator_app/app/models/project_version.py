from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4

from generator_app.app.core.database import Base


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    version = Column(Integer, nullable=False)
    definition_json = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    project = relationship("Project", back_populates="versions")
