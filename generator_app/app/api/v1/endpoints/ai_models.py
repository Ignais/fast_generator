from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from generator_app.app.schemas.ai_model import AIModelCreate, AIModelUpdate, AIModelResponse
from generator_app.app.services.ai_model_service import (
    create_ai_model, get_ai_model, list_ai_models, update_ai_model, delete_ai_model
)
from generator_app.app.core.database import get_db
from generator_app.app.core.security import get_current_user
from generator_app.app.models.user import User

router = APIRouter(prefix="/ai-models", tags=["AI Models"])


@router.post("/", response_model=AIModelResponse)
def create_model(payload: AIModelCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = create_ai_model(db, payload)
    return model


@router.get("/", response_model=List[AIModelResponse])
def list_models(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_ai_models(db)


@router.get("/{model_id}", response_model=AIModelResponse)
def get_model(model_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = get_ai_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{model_id}", response_model=AIModelResponse)
def update_model(model_id: UUID, payload: AIModelUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = update_ai_model(db, model_id, payload)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.delete("/{model_id}")
def delete_model(model_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ok = delete_ai_model(db, model_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"deleted": True}
