from typing import Dict, Any
from ..base import AIProvider

class TutorAgent:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def explain_or_hint(self, prompt: str, mode: str = "explain", context: str = "") -> Dict[str, Any]:
        """
        mode: 'explain', 'hint', 'socratic'
        """
        if mode == "hint":
            system_prompt = (
                "You are SolveNow's Master Tutor. The user wants a hint rather than the complete solution. "
                "Provide a targeted, thought-provoking hint that guides them toward the answer on their own without spoiling it."
            )
        else:
            system_prompt = (
                "You are SolveNow's Master Tutor. Explain foundational concepts, intuition, and mental models "
                "clearly. Use analogies, breaking complex topics into intuitive digestible steps."
            )

        if context:
            system_prompt += f"\n\nContext:\n{context}"

        response = self.provider.generate_chat_response(prompt=prompt, system_prompt=system_prompt)
        return {
            "final_answer": response,
            "activity_steps": [
                {"step": "Tutor Guidance", "description": f"Provided {mode} tailored to student context."}
            ],
            "agent_role": "Pedagogical Concept & Socratic Tutor"
        }

