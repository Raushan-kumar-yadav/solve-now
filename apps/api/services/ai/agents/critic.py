from .base import BaseAgent
from schemas.ai import CriticReviewOutput
import json

class CriticAgent(BaseAgent):
    def review(self, problem_description: str, findings: list, proposed_solution: dict) -> CriticReviewOutput:
        system_prompt = (
            "You are the Critic Agent. You are adversarial. Your job is to actively challenge the proposed solution. "
            "Identify missing evidence, logical contradictions, unsafe instructions, and weak assumptions. "
            "Ensure the AI does not recommend destructive operations."
        )
        
        prompt = f"""
        Problem: {problem_description}
        Diagnostic Findings: {json.dumps(findings)}
        Proposed Solution: {json.dumps(proposed_solution)}
        
        Provide your ruthless, adversarial review of the proposed solution.
        """
        
        return self.run(prompt, CriticReviewOutput, system_prompt)

