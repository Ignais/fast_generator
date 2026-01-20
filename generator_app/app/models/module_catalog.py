from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

from generator_app.app.core.database import Base


class ModuleCatalog(Base):
    __tablename__ = "modules_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    description = Column(String)

    definition_json = Column(JSON, nullable=False)

    is_global = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
