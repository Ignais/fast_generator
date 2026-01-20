from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str

    # OpenAI (opcional)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str | None = None

    # Proveedor dinámico
    AI_PROVIDER: str = "openai"

    # DeepSeek
    DEEPSEEK_API_KEY: str | None = None
    DEEPSEEK_MODEL: str | None = None

    # Groq
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str | None = None

    # Together
    TOGETHER_API_KEY: str | None = None
    TOGETHER_MODEL: str | None = None

    # Mistral
    MISTRAL_API_KEY: str | None = None
    MISTRAL_MODEL: str | None = None

    # OpenRouter
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str | None = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()
