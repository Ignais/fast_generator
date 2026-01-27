import asyncio
import logging
from typing import List, Dict, Any

from fastapi.params import Depends
from sqlalchemy.orm import Session
from openai import OpenAI

from generator_app.app.core.database import get_db
from generator_app.app.models.ai_model import AIModel
from generator_app.app.services.ai_model_service import AIModelService
from generator_app.app.core.config import settings

logger = logging.getLogger("fastapi_app")


class AIClientService:
    """Service responsible for building clients from AIModel entries and performing calls with fallback."""

    def __init__(self, db: Session):
        self.db = db

    def _build_client_for(self, ai_model: AIModel) -> OpenAI:
        provider = (ai_model.provider or settings.AI_PROVIDER).lower()

        # Base URLs por proveedor
        provider_urls = {
            "groq": "https://api.groq.com/openai/v1",
            "deepseek": "https://api.deepseek.com",
            "together": "https://api.together.xyz/v1",
            "mistral": "https://api.mistral.ai/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "openai": None,  # usa el default del SDK
        }

        base_url = provider_urls.get(provider)
        api_key = ai_model.api_key or getattr(settings, f"{provider.upper()}_API_KEY", None)

        if not api_key:
            raise RuntimeError(f"No API key configured for provider: {provider}")

        # Headers obligatorios para OpenRouter
        default_headers = {}
        if provider == "openrouter":
            default_headers = {
                "HTTP-Referer": settings.APP_URL or "http://localhost:8000",
                "X-Title": settings.APP_NAME or "FastGenerator",
            }

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=default_headers
        )

        # Wrapper async para clientes sync
        if hasattr(client, "chat") and not hasattr(client.chat, "completions_async"):
            class AsyncWrapper:
                def __init__(self, sync_client):
                    self._sync = sync_client

                async def chat_completions_create(self, *args, **kwargs):
                    from fastapi.concurrency import run_in_threadpool
                    return await run_in_threadpool(
                        lambda: self._sync.chat.completions.create(*args, **kwargs)
                    )

            client.async_chat_completions_create = AsyncWrapper(client).chat_completions_create

        return client

    def get_active_models(self) -> List[AIModel]:
        return AIModelService.list(self.db)

    async def call_with_fallback(self, payload: Dict[str, Any]) -> Any:
        from fastapi.concurrency import run_in_threadpool

        models = await run_in_threadpool(
            lambda: [m for m in self.get_active_models() if m.is_active]
        )

        last_exc = None

        for ai_model in models:
            client = self._build_client_for(ai_model)

            if ai_model.model_name:
                payload["model"] = ai_model.model_name

            try:
                logger.info(f"IA: intentando proveedor {ai_model.provider} con modelo {payload.get('model')}")

                if hasattr(client, "async_chat_completions_create"):
                    resp = await client.async_chat_completions_create(**payload)
                    logger.info(f"{resp.json()}")
                else:
                    resp = await run_in_threadpool(
                        lambda: client.chat.completions.create(**payload)
                    )

                return resp

            except Exception as e:
                logger.error(f"IA: Error con modelo {ai_model.name} ({ai_model.provider}): {repr(e)}")
                last_exc = e
                continue

        if last_exc:
            raise last_exc

        raise RuntimeError("No AI models configured in DB")

# helper dependency provider
def get_ai_client_service(db: Session = Depends(get_db)):
    return AIClientService(db)
