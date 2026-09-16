import os
import openai
from core.config import settings
from .base import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self):
        api_key = settings.AI_API_KEY or os.environ.get("OPENAI_API_KEY", "") or os.environ.get("AI_API_KEY", "")
        if not api_key:
            raise ValueError("OpenAI API key is not configured. Please set AI_API_KEY or OPENAI_API_KEY in .env")
        self.client = openai.Client(api_key=api_key)
        self.model = settings.AI_MODEL or "gpt-4o-mini"

    def generate_chat_response(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
