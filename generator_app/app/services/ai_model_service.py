from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from generator_app.app.models.ai_model import AIModel
from generator_app.app.schemas.ai_model import AIModelCreate, AIModelUpdate


class AIModelService:
    """Service class to manage AIModel CRUD operations."""

    @staticmethod
    def create(db: Session, payload: AIModelCreate) -> AIModel:
        model = AIModel(
            name=payload.name,
            provider=payload.provider,
            api_key=payload.api_key,
            model_name=payload.model_name,
            is_active=payload.is_active if payload.is_active is not None else True
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    @staticmethod
    def get(db: Session, model_id: UUID) -> AIModel | None:
        return db.query(AIModel).filter(AIModel.id == model_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> AIModel | None:
        return db.query(AIModel).filter(AIModel.name == name).first()

    @staticmethod
    def list(db: Session) -> List[AIModel]:
        return db.query(AIModel).order_by(AIModel.created_at.asc()).all()

    @staticmethod
    def update(db: Session, model_id: UUID, payload: AIModelUpdate) -> AIModel | None:
        model = db.query(AIModel).filter(AIModel.id == model_id).first()
        if not model:
            return None
        for k, v in payload.dict(exclude_unset=True).items():
            setattr(model, k, v)
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    @staticmethod
    def delete(db: Session, model_id: UUID) -> bool:
        model = db.query(AIModel).filter(AIModel.id == model_id).first()
        if not model:
            return False
        db.delete(model)
        db.commit()
        return True


# Backwards-compatible helper functions

def create_ai_model(db: Session, payload: AIModelCreate) -> AIModel:
    return AIModelService.create(db, payload)


def get_ai_model(db: Session, model_id: UUID) -> AIModel | None:
    return AIModelService.get(db, model_id)


def get_ai_model_by_name(db: Session, name: str) -> AIModel | None:
    return AIModelService.get_by_name(db, name)


def list_ai_models(db: Session) -> List[AIModel]:
    return AIModelService.list(db)


def update_ai_model(db: Session, model_id: UUID, payload: AIModelUpdate) -> AIModel | None:
    return AIModelService.update(db, model_id, payload)


def delete_ai_model(db: Session, model_id: UUID) -> bool:
    return AIModelService.delete(db, model_id)
