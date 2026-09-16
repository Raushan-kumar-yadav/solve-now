from core.config import settings
from .base import AIProvider
from .gemini import GeminiProvider
from .openai_provider import OpenAIProvider

def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return GeminiProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unsupported AI Provider: {settings.AI_PROVIDER}")
