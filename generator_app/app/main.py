from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from generator_app.app.core.logging_config import logger
from generator_app.app.api.v1.endpoints.generate import router as generate_router
from generator_app.app.api.v1.endpoints.auth import router as auth_router
from generator_app.app.api.v1.endpoints.projects import router as project_router
from generator_app.app.api.v1.endpoints.ai import router as ai_router
from generator_app.app.api.v1.endpoints.permissions import router as permissions_router
from generator_app.app.api.v1.endpoints.role import router as roles_router
from generator_app.app.core.database import Base, engine

def create_app():
    app = FastAPI()

    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    # Registrar middleware de excepciones
    @app.middleware("http")
    async def log_exceptions(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse( status_code=500, content={"detail": "Internal Server Error"} )

    return app



app = create_app()

app.include_router(generate_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(permissions_router, prefix="/api/v1")
app.include_router(roles_router, prefix="/api/v1")
