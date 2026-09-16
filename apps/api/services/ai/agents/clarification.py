from .base import BaseAgent
from schemas.ai import ClarificationOutput
import json

class ClarificationAgent(BaseAgent):
    def clarify(self, problem_description: str, intake_data: dict, previous_clarifications: list) -> ClarificationOutput:
        system_prompt = (
            "You are the Clarification Agent. Your job is to determine if the user has provided "
            "enough information to properly diagnose the problem. If information is missing, formulate "
            "precise clarifying questions."
        )
        
        prompt = f"""
        Problem: {problem_description}
        Intake Data: {json.dumps(intake_data)}
        Previous Clarifications (Answered): {json.dumps(previous_clarifications)}
        
        Analyze the problem and determine if more info is needed.
        """
        
        return self.run(prompt, ClarificationOutput, system_prompt)

