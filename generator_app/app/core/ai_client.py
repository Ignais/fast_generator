from openai import OpenAI
from generator_app.app.core.config import settings


def get_ai_client():
    provider = settings.AI_PROVIDER.lower()

    if provider == "groq":
        return OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

    if provider == "deepseek":
        return OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )

    if provider == "together":
        return OpenAI(
            api_key=settings.TOGETHER_API_KEY,
            base_url="https://api.together.xyz/v1"
        )

    if provider == "mistral":
        return OpenAI(
            api_key=settings.MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )

    if provider == "openrouter":
        return OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://api.openrouter.ai/v1"
        )

    # Default: OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)


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
