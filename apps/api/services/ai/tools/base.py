from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool description"

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Execute the tool and return the string output."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description
        }

