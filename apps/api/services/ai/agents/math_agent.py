from typing import Dict, Any
from ..base import AIProvider
from ..engine.react_agent import SolveNowReactAgent
from ..tools.python_repl import PythonREPLTool

class MathAgent:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.tools = [PythonREPLTool()]
        self.agent = SolveNowReactAgent(
            provider=self.provider,
            tools=self.tools,
            role_name="Mathematical & Algorithmic Reasoning Specialist"
        )

    def calculate_and_prove(self, problem: str, context: str = "") -> Dict[str, Any]:
        system_context = (
            "You are a mathematician and algorithmic computation expert. "
            "Always verify complex calculations, algebra, statistics, or numerical solutions "
            "by executing code in the Python REPL tool. "
            "Show clear step-by-step proofs and derivations alongside exact numerical answers."
        )
        if context:
            system_context += f"\n\nContext:\n{context}"

        return self.agent.run(prompt=problem, system_context=system_context)
