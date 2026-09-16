from typing import Dict, Any
from ..base import AIProvider
from ..engine.react_agent import SolveNowReactAgent
from ..tools.python_repl import PythonREPLTool
from ..tools.web_search import WebSearchTool

class DebuggingAgent:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.tools = [PythonREPLTool(), WebSearchTool()]
        self.agent = SolveNowReactAgent(
            provider=self.provider,
            tools=self.tools,
            role_name="Root-Cause Debugging & Diagnostics Expert"
        )

    def diagnose_and_fix(self, error_message: str, code_snippet: str = "", context: str = "") -> Dict[str, Any]:
        prompt = f"Debug and resolve the following issue:\n\nError/Logs:\n{error_message}"
        if code_snippet:
            prompt += f"\n\nSource Code:\n{code_snippet}"

        system_context = (
            "You are a principal systems troubleshooter and debugging expert. "
            "1. Pinpoint the exact root cause of the error or failure.\n"
            "2. Identify reproduction conditions.\n"
            "3. Use Python REPL to test the fix if applicable, or web search to verify version quirks.\n"
            "4. Provide the exact patched code and instructions to prevent recurrence."
        )
        if context:
            system_context += f"\n\nAdditional Problem Context:\n{context}"

        return self.agent.run(prompt=prompt, system_context=system_context)

