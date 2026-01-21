from fastapi import APIRouter, Depends, HTTPException
from generator_app.app.core.security import get_current_user
from generator_app.app.models.user import User
from generator_app.app.core.ai_client import get_ai_client, get_ai_model
import json
import logging
from generator_app.app.workers.clean_json import extract_json

from generator_app.app.schemas.ai import AIGenerateResponse, AIGenerateRequest

router = APIRouter(prefix="/ai", tags=["AI"])

logger = logging.getLogger("fastapi_app")


@router.post("/generate-project", response_model=AIGenerateResponse)
def generate_project_ai(
    payload: AIGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info("IA: Prompt recibido para generación de proyecto")

        client = get_ai_client()
        model = get_ai_model()

        logger.info(f"IA: Usando proveedor con modelo: {model}")

        response = client.chat.completions.create(
            model=model,
            messages=[
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
            ],
            temperature=0.2
        )

        raw_output = response.choices[0].message.content
        logger.info(f"IA: Respuesta cruda recibida: {raw_output}")

        # Validación JSON
        try:
            definition = json.loads(raw_output)
        except Exception as e:
            logger.error(f"IA: Error al parsear JSON: {e}")
            raise HTTPException(
                status_code=500,
                detail="La IA devolvió un formato inválido. Intenta reformular el prompt."
            )

        logger.info("IA: JSON válido generado correctamente")

        return {"definition_json": definition}

    except Exception as e:
        logger.error(f"IA: Error inesperado: {e}")
        err_str = str(e)
        if "401" in err_str or "User not found" in err_str or "'code': 401" in err_str:
            raise HTTPException(status_code=401, detail="Error de autenticación con el proveedor de IA. Verifica la clave API.")
        raise HTTPException(status_code=500, detail=f"Error al generar proyecto con IA: {e}")
