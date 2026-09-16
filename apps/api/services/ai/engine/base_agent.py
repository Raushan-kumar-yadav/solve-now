from typing import List, Dict, Any, Tuple
from ..base import AIProvider
from ..tools.base import BaseTool

class BaseExecutionAgent:
    def __init__(self, provider: AIProvider, tools: List[BaseTool] = None, max_iter: int = 5):
        self.provider = provider
        self.tools_map: Dict[str, BaseTool] = {t.name: t for t in (tools or [])}
        self.max_iter = max_iter
        self.history: List[Tuple[str, str]] = []
        self.activity_steps: List[Dict[str, Any]] = []

    def log_activity(self, step_type: str, description: str, data: Any = None):
        self.activity_steps.append({
            "step": step_type,
            "description": description,
            "data": data
        })

    @property
    def tool_descriptions(self) -> str:
        if not self.tools_map:
            return "No external tools available."
        desc = []
        for name, tool in self.tools_map.items():
            desc.append(f"- {name}: {tool.description}")
        return "\n".join(desc)

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        if tool_name not in self.tools_map:
            return f"Error: Tool '{tool_name}' not found."
        tool = self.tools_map[tool_name]
        try:
            return tool.run(**kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
