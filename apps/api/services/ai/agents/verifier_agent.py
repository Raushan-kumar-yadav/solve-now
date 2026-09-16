from typing import Dict, Any
from ..base import AIProvider

class VerifierAgent:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def verify_solution(self, original_problem: str, proposed_solution: str, context: str = "") -> Dict[str, Any]:
        system_prompt = (
            "You are SolveNow's Senior Quality & Security Auditor. "
            "Critically analyze the proposed solution against the original problem.\n"
            "Evaluate:\n"
            "1. Correctness: Does it accurately address all requirements?\n"
            "2. Edge Cases: Are there hidden edge cases or failure modes?\n"
            "3. Security & Safety: Does it introduce vulnerabilities or dangerous operations?\n"
            "4. Verdict: Explicitly conclude with either [APPROVED] or [REVISION NEEDED] with specific actionable improvements."
        )

        audit_prompt = (
            f"Original Problem:\n{original_problem}\n\n"
            f"Proposed Solution:\n{proposed_solution}\n"
        )
        if context:
            audit_prompt += f"\nAdditional Context:\n{context}"

        response = self.provider.generate_chat_response(prompt=audit_prompt, system_prompt=system_prompt)
        is_approved = "[APPROVED]" in response or "approved" in response.lower()

        return {
            "final_answer": response,
            "is_approved": is_approved,
            "activity_steps": [
                {"step": "Verification Audit", "description": f"Audit completed with verdict: {'APPROVED' if is_approved else 'REVISION SUGGESTED'}"}
            ],
            "agent_role": "Quality Assurance & Solution Verifier"
        }

