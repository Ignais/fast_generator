from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings


# -----------------------------
# SQLAlchemy Base
# -----------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------
# Engine
# -----------------------------
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,          # puedes activar logs si deseas
    future=True
)


# -----------------------------
# SessionLocal
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)


# -----------------------------
# Dependency get_db()
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
