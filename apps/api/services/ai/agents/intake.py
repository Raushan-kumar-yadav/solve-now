from .base import BaseAgent
from schemas.ai import IntakeOutput

class IntakeAgent(BaseAgent):
    def analyze(self, problem_description: str) -> IntakeOutput:
        system_prompt = (
            "You are the Intake Agent. Your job is to structure raw user problem descriptions "
            "into a formal category, subcategory, concise summary, and urgency level."
        )
        return self.run(problem_description, IntakeOutput, system_prompt)

