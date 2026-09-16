from .base import BaseAgent
from schemas.ai import SolutionOutput
import json

class SolutionAgent(BaseAgent):
    def generate_solutions(self, problem_description: str, findings: list) -> SolutionOutput:
        system_prompt = (
            "You are the Solution Agent. Your job is to propose actionable, step-by-step mitigation strategies "
            "based on the diagnostic findings. Formulate clear titles, detailed descriptions, and steps."
        )
        
        prompt = f"""
        Problem: {problem_description}
        Diagnostic Findings: {json.dumps(findings)}
        
        Propose solutions.
        """
        
        return self.run(prompt, SolutionOutput, system_prompt)

