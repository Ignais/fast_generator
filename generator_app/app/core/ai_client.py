from openai import OpenAI
from generator_app.app.core.config import settings


def get_ai_client():
    provider = settings.AI_PROVIDER.lower()

    if provider == "groq":
        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        # agregar wrapper async si la librería lo soporta
        if hasattr(client, "chat") and not hasattr(client.chat, "completions_async"):
            # provide an async wrapper using run_in_executor
            class AsyncWrapper:
                def __init__(self, sync_client):
                    self._sync = sync_client

                async def chat_completions_create(self, *args, **kwargs):
                    import asyncio
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, lambda: self._sync.chat.completions.create(*args, **kwargs))

            client.async_chat_completions_create = AsyncWrapper(client).chat_completions_create
        return client

    if provider == "deepseek":
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        return client

    if provider == "together":
        client = OpenAI(
            api_key=settings.TOGETHER_API_KEY,
            base_url="https://api.together.xyz/v1"
        )
        return client

    if provider == "mistral":
        client = OpenAI(
            api_key=settings.MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )
        return client

    if provider == "openrouter":
        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://api.openrouter.ai/v1"
        )
        return client

    # Default: OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    if hasattr(client, "chat") and not hasattr(client.chat, "completions_async"):
        class AsyncWrapper:
            def __init__(self, sync_client):
                self._sync = sync_client

            async def chat_completions_create(self, *args, **kwargs):
                import asyncio
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: self._sync.chat.completions.create(*args, **kwargs))

        client.async_chat_completions_create = AsyncWrapper(client).chat_completions_create

    return client


def get_ai_model():
    provider = settings.AI_PROVIDER.lower()

    if provider == "deepseek":
        return settings.DEEPSEEK_MODEL

    if provider == "groq":
        return settings.GROQ_MODEL

    if provider == "together":
        return settings.TOGETHER_MODEL

    if provider == "mistral":
        return settings.MISTRAL_MODEL

    if provider == "openrouter":
        return settings.OPENROUTER_MODEL

    # Default: OpenAI
    return settings.OPENAI_MODEL
