from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4

from generator_app.app.core.database import Base


class ProjectCollaborator(Base):
    __tablename__ = "project_collaborators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    role = Column(String, nullable=False)  # owner, editor, viewer

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    project = relationship("Project", back_populates="collaborators")
    user = relationship("User")
