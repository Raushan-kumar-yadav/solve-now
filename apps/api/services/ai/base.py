from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_chat_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a raw text response for chat/hints."""
        pass
