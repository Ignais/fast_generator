from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from generator_app.app.core.database import get_db
from generator_app.app.core.logging_config import logger
from generator_app.app.core.security import hash_password, verify_password, create_access_token, get_current_user
from generator_app.app.models.user import User
from generator_app.app.schemas.auth import UserCreate, UserLogin, Token
from generator_app.app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    logger.warning(f"PAYLOAD RECIBIDO: {payload}")

    try:
        logger.warning(f"PASSWORD RAW: {repr(payload.password)}")
    except Exception as e:
        logger.error(f"Error leyendo password: {e}")

    if len(payload.password.encode("utf-8")) > 72:
        logger.error("Password demasiado largo")
        raise HTTPException(status_code=400, detail="Password too long")

    try:
        existing = db.query(User).filter(User.email == payload.email).first()
        logger.warning(f"EXISTING USER: {existing}")
    except Exception as e:
        logger.error(f"Error consultando DB: {e}", exc_info=True)
        raise

    try:
        hashed = hash_password(payload.password)
        logger.warning(f"HASH GENERADO: {hashed}")
    except Exception as e:
        logger.error(f"Error hasheando password: {e}", exc_info=True)
        raise

    try:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hashed
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.warning(f"USUARIO CREADO: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error guardando usuario: {e}", exc_info=True)
        raise

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Intento de login para email: {payload.email}")
    try:
        user = db.query(User).filter(User.email == payload.email).first()
        logger.debug(f"Resultado de búsqueda de usuario: {user}")
    except Exception as e:
        logger.error(f"Error consultando usuario en DB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")

    if not user:
        logger.warning(f"Login fallido: usuario no encontrado ({payload.email})")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    try:
        password_ok = verify_password(payload.password, user.password_hash)
        logger.debug(f"Resultado verificación password: {password_ok}")
    except Exception as e:
        logger.error(f"Error verificando password: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Password verification error")

    if not password_ok:
        logger.warning(f"Login fallido: contraseña incorrecta ({payload.email})")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    try:
        token = create_access_token({"sub": str(user.id)})
        logger.info(f"Login exitoso para usuario ID={user.id}")
    except Exception as e:
        logger.error(f"Error generando token JWT: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Token generation error")

    return Token(access_token=token)

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
