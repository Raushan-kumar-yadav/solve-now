import os
from core.config import settings
from .base import AIProvider
from .gemini import GeminiProvider
from .openai_provider import OpenAIProvider
from .fallback_provider import FallbackAIProvider

def get_ai_provider() -> AIProvider:
    api_key = settings.AI_API_KEY or os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "") or os.environ.get("AI_API_KEY", "")
    if not api_key:
        return FallbackAIProvider()

    provider = settings.AI_PROVIDER.lower()
    try:
        if provider == "gemini":
            return GeminiProvider()
        elif provider == "openai":
            return OpenAIProvider()
        else:
            return FallbackAIProvider()
    except Exception:
        return FallbackAIProvider()
