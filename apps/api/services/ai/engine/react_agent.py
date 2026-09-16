import json
import re
from typing import List, Dict, Any
from .base_agent import BaseExecutionAgent
from ..base import AIProvider
from ..tools.base import BaseTool

class SolveNowReactAgent(BaseExecutionAgent):
    def __init__(self, provider: AIProvider, tools: List[BaseTool] = None, role_name: str = "Specialized Agent", max_iter: int = 4):
        super().__init__(provider=provider, tools=tools, max_iter=max_iter)
        self.role_name = role_name

    def run(self, prompt: str, system_context: str = "") -> Dict[str, Any]:
        """
        Executes the ReAct reasoning loop.
        Returns a dict:
        {
            "final_answer": str,
            "activity_steps": List[Dict],
            "agent_role": str
        }
        """
        self.activity_steps = []
        self.log_activity("Agent Activated", f"{self.role_name} activated for problem processing.")

        if not self.tools_map:
            # Direct generation if no tools are assigned
            full_system = f"You are SolveNow's {self.role_name}.\n{system_context}"
            answer = self.provider.generate_chat_response(prompt=prompt, system_prompt=full_system)
            self.log_activity("Generation Complete", f"{self.role_name} produced direct solution.")
            return {
                "final_answer": answer,
                "activity_steps": self.activity_steps,
                "agent_role": self.role_name
            }

        iteration = 0
        context_history = [f"Problem/Task: {prompt}"]

        while iteration < self.max_iter:
            iteration += 1

            react_system_prompt = (
                f"You are SolveNow's {self.role_name}.\n"
                f"{system_context}\n\n"
                f"Available Tools:\n{self.tool_descriptions}\n\n"
                "Respond strictly with a JSON object in one of two formats:\n"
                "1. If you need to use a tool to gather info or calculate:\n"
                "{\n"
                '  "action": "tool_call",\n'
                '  "tool": "<tool_name>",\n'
                '  "argument": "<query_or_code_or_url>",\n'
                '  "thought": "<reasoning for using this tool>"\n'
                "}\n"
                "2. If you have sufficient information to provide the final complete response:\n"
                "{\n"
                '  "action": "final_answer",\n'
                '  "thought": "<summary of conclusion>",\n'
                '  "answer": "<detailed solution/response for user>"\n'
                "}"
            )

            current_prompt = (
                "Review the history and decide the next step.\n\n"
                + "\n\n".join(context_history)
            )

            raw_response = self.provider.generate_chat_response(prompt=current_prompt, system_prompt=react_system_prompt)
            
            # Extract JSON from model output
            parsed = self._extract_json(raw_response)

            if not parsed or parsed.get("action") == "final_answer":
                final_ans = parsed.get("answer") if parsed else raw_response
                self.log_activity("Solution Verified", f"{self.role_name} formulated the final solution.")
                return {
                    "final_answer": final_ans,
                    "activity_steps": self.activity_steps,
                    "agent_role": self.role_name
                }

            if parsed.get("action") == "tool_call":
                tool_name = parsed.get("tool")
                arg = parsed.get("argument", "")
                thought = parsed.get("thought", "")

                self.log_activity("Tool Call", f"Using tool '{tool_name}'", {"thought": thought, "argument": str(arg)[:200]})
                
                # Execute tool
                tool_output = self.execute_tool(tool_name, query=arg, code=arg, url=arg)
                truncated_output = tool_output[:1500] if len(tool_output) > 1500 else tool_output
                
                self.log_activity("Tool Result", f"Output received from '{tool_name}'", {"output_sample": truncated_output[:250]})
                
                context_history.append(f"Thought: {thought}\nTool Call: {tool_name}({arg})\nObservation: {truncated_output}")

        # If max iterations reached, synthesize final answer
        summary_prompt = (
            "Based on the following observations, provide a comprehensive final answer to the user's task:\n\n"
            + "\n\n".join(context_history)
        )
        final_answer = self.provider.generate_chat_response(prompt=summary_prompt, system_prompt=f"You are SolveNow's {self.role_name}.\n{system_context}")
        self.log_activity("Solution Synthesized", f"{self.role_name} synthesized final response from gathered data.")

        return {
            "final_answer": final_answer,
            "activity_steps": self.activity_steps,
            "agent_role": self.role_name
        }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            # Direct match
            return json.loads(text.strip())
        except Exception:
            pass

        # Try regex search for markdown ```json blocks
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        # Try finding outer braces
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass

        return None

