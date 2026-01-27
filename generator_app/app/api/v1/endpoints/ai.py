from fastapi import APIRouter, Depends, HTTPException
from generator_app.app.core.security import get_current_user
from generator_app.app.core.database import get_db
from generator_app.app.schemas.ai import AIGenerateRequest, AIGenerateResponse
from generator_app.app.services.ai_client_service import AIClientService
from generator_app.app.models.user import User
import json
import logging

from generator_app.app.workers import extract_ai_content, clean_json_output

logger = logging.getLogger("fastapi_app")

router = APIRouter(prefix="/ai", tags=["AI"])

# ---------------------------------------------------------
# ENDPOINT PRINCIPAL
# ---------------------------------------------------------
@router.post("/generate-project", response_model=AIGenerateResponse)
async def generate_project_ai(
    payload: AIGenerateRequest,
    current_user: User = Depends(get_current_user),
    client_service: AIClientService = Depends(lambda db=Depends(get_db): AIClientService(db))
):
    try:
        logger.info("IA: Prompt recibido para generación de proyecto")

        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un generador experto de proyectos FastAPI. "
                    "Tu salida SIEMPRE debe ser un JSON válido con dos claves: "
                    "'project' y 'models'. "
                    "No incluyas explicaciones, solo JSON puro."
                )
            },
            {"role": "user", "content": payload.prompt}
        ]

        # Llamada con fallback
        response = await client_service.call_with_fallback({
            "messages": messages,
            "temperature": 0.2
        })

        # Extraer contenido universal
        raw_output = extract_ai_content(response)
        logger.info(f"IA: Respuesta cruda recibida: {raw_output}")

        # Limpiar JSON
        cleaned = clean_json_output(raw_output)
        logger.info(f"IA: JSON limpio: {cleaned}")

        # Validar JSON
        try:
            definition = json.loads(cleaned)
        except Exception as e:
            logger.error(f"IA: Error al parsear JSON: {e}")
            raise HTTPException(
                status_code=500,
                detail="La IA devolvió un formato inválido. Intenta reformular el prompt."
            )

        logger.info("IA: JSON válido generado correctamente")

        return {"definition_json": definition}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"IA: Error inesperado: {e}")
        err_str = str(e)
        if "401" in err_str or "User not found" in err_str or "'code': 401" in err_str:
            raise HTTPException(status_code=401, detail="Error de autenticación con el proveedor de IA. Verifica la clave API.")
        raise HTTPException(status_code=500, detail=f"Error al generar proyecto con IA: {e}")
