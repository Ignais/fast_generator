from fastapi import APIRouter, Depends, HTTPException
from generator_app.app.core.security import get_current_user
from generator_app.app.models.user import User
from generator_app.app.schemas.ai import AIGenerateResponse, AIGenerateRequest
from generator_app.app.core.ai_client import get_ai_client, get_ai_model
from generator_app.app.core.audit_logger import audit
from generator_app.app.schemas.normalized_definition import NormalizedDefinition
from generator_app.app.workers.clean_json import extract_json
from generator_app.app.workers.normalizer import normalize_project_definition

router = APIRouter(prefix="/ai", tags=["AI"])

client = get_ai_client()
model = get_ai_model()

@router.post("/generate-project", response_model=AIGenerateResponse)
def generate_project_ai(
    payload: AIGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    # AUDIT: Prompt recibido
    audit(
        user_id=current_user.id,
        action="AI_PROMPT_RECEIVED",
        data={"prompt": payload.prompt}
    )

    # 1. Llamada al modelo
    try:
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

        # AUDIT: Respuesta cruda de la IA
        audit(
            user_id=current_user.id,
            action="AI_RAW_RESPONSE",
            data={"raw_output": raw_output}
        )

    except Exception as e:
        audit(
            user_id=current_user.id,
            action="AI_ERROR",
            data={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Error al comunicarse con el modelo de IA")

    # 2. Parsear JSON
    try:
        definition = extract_json(raw_output)
    except Exception as e:
        audit(
            user_id=current_user.id,
            action="AI_JSON_PARSE_ERROR",
            data={"error": str(e), "raw_output": raw_output}
        )
        raise HTTPException(status_code=500, detail="La IA devolvió un formato inválido.")

    # 3. Normalizar
    normalized = normalize_project_definition(definition)

    # AUDIT: JSON normalizado
    audit(
        user_id=current_user.id,
        action="AI_JSON_NORMALIZED",
        data=normalized
    )

    # 4. Validar con Pydantic
    validated = NormalizedDefinition(**normalized)

    # AUDIT: Warnings generados
    audit(
        user_id=current_user.id,
        action="AI_WARNINGS",
        data={"warnings": validated.warnings}
    )

    return validated

