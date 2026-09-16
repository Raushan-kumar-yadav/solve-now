from typing import Dict, Any, List
from ..base import AIProvider
from ..engine.react_agent import SolveNowReactAgent
from ..tools.python_repl import PythonREPLTool

class CodingAgent:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.tools = [PythonREPLTool()]
        self.agent = SolveNowReactAgent(
            provider=self.provider,
            tools=self.tools,
            role_name="Software Engineering & Coding Specialist"
        )

    def solve(self, prompt: str, code_context: str = "", files_context: str = "") -> Dict[str, Any]:
        system_context = (
            "You are an elite software architect and senior developer. "
            "Write clean, idiomatic, production-ready code with type annotations and error handling. "
            "You have access to a Python REPL tool to test and validate code logic and algorithmic correctness."
        )
        if code_context:
            system_context += f"\n\nExisting Codebase Context:\n{code_context}"
        if files_context:
            system_context += f"\n\nAttached Files:\n{files_context}"

        return self.agent.run(prompt=prompt, system_context=system_context)
