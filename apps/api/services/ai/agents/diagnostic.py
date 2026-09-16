from .base import BaseAgent
from schemas.ai import DiagnosticOutput
import json

class DiagnosticAgent(BaseAgent):
    def diagnose(self, problem_description: str, intake_data: dict, clarifications: list) -> DiagnosticOutput:
        system_prompt = (
            "You are the Diagnostic Agent. Your job is to analyze the provided problem, context, and clarifications, "
            "and generate factual findings and potential root causes. Every finding must have an explicit confidence "
            "score (0.0 to 1.0) and specify the exact evidence supporting it."
        )
        
        prompt = f"""
        Problem: {problem_description}
        Intake Data: {json.dumps(intake_data)}
        Clarifications: {json.dumps(clarifications)}
        
        Generate the diagnostic findings. Do not hallucinate evidence.
        """
        
        return self.run(prompt, DiagnosticOutput, system_prompt)

