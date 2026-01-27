# Deprecated compatibility module. Prefer using generator_app.app.services.ai_client_service.AIClientService
from generator_app.app.services.ai_client_service import AIClientService, get_ai_client_service

# provide a compatibility call helper that will construct a service instance using the request DB session
async def call_with_fallback(db, **kwargs):
    service = AIClientService(db)
    return await service.call_with_fallback(kwargs)


def get_ai_client():
    # small helper that builds a client using env defaults
    from generator_app.app.models.ai_model import AIModel
    from generator_app.app.core.config import settings
    dummy = AIModel(
        id=None,
        name="env_default",
        provider=settings.AI_PROVIDER,
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.OPENAI_MODEL,
        is_active=True
    )
    return AIClientService(None)._build_client_for(dummy)


def get_ai_model():
    from generator_app.app.core.config import settings
    return settings.OPENAI_MODEL
