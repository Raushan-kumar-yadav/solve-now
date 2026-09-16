import json
import re
from typing import Dict, Any, Optional
from ..base import AIProvider
from .coding_agent import CodingAgent
from .debugging_agent import DebuggingAgent
from .research_agent import ResearchAgent
from .math_agent import MathAgent
from .tutor_agent import TutorAgent
from .verifier_agent import VerifierAgent

class ProblemOrchestrator:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.coding_agent = CodingAgent(provider)
        self.debugging_agent = DebuggingAgent(provider)
        self.research_agent = ResearchAgent(provider)
        self.math_agent = MathAgent(provider)
        self.tutor_agent = TutorAgent(provider)
        self.verifier_agent = VerifierAgent(provider)

    def classify_intent(self, message: str, context: str = "") -> str:
        """
        Determines the most suitable agent for the task.
        Returns one of: 'coding', 'debugging', 'research', 'math', 'tutor', 'verifier'
        """
        system_prompt = (
            "You are SolveNow's Master Dispatcher. Classify the user query into exactly ONE category:\n"
            "- 'debugging': stack traces, exceptions, bugs, error messages, why something failed.\n"
            "- 'coding': code generation, implementation, refactoring, algorithms, programming.\n"
            "- 'math': calculations, statistics, algebra, mathematical proofs, geometry.\n"
            "- 'research': literature, academic papers, general facts, Wikipedia, market research.\n"
            "- 'tutor': requests for hints, high-level conceptual explanations, learning guidance.\n"
            "- 'verifier': reviewing an existing solution for correctness or safety.\n\n"
            "Respond ONLY with a JSON object: {\"category\": \"<one_of_the_above>\", \"reason\": \"<short_reason>\"}"
        )

        query = f"Task: {message}"
        if context:
            query += f"\nContext: {context[:500]}"

        try:
            raw = self.provider.generate_chat_response(prompt=query, system_prompt=system_prompt)
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                cat = data.get("category", "").lower().strip()
                if cat in ["debugging", "coding", "math", "research", "tutor", "verifier"]:
                    return cat
        except Exception:
            pass

        # Heuristic fallback
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["traceback", "error", "exception", "failed", "bug", "crash", "401", "404", "500"]):
            return "debugging"
        if any(w in msg_lower for w in ["calculate", "math", "equation", "solve for x", "integral", "derivative"]):
            return "math"
        if any(w in msg_lower for w in ["paper", "research", "arxiv", "history", "who is", "what is the capital"]):
            return "research"
        if any(w in msg_lower for w in ["hint", "explain", "concept", "teach"]):
            return "tutor"
        if any(w in msg_lower for w in ["review", "audit", "verify"]):
            return "verifier"
        return "coding"

    def orchestrate(
        self,
        message: str,
        problem_context: str = "",
        forced_agent: Optional[str] = None,
        verify_result: bool = True
    ) -> Dict[str, Any]:
        """
        Full orchestration flow:
        1. Classify
        2. Execute specialized agent with tools
        3. Optional verification
        4. Package solution and activity trace
        """
        activity_steps = []

        agent_type = forced_agent or self.classify_intent(message, problem_context)
        activity_steps.append({
            "step": "Problem Classification",
            "description": f"Classified problem type as: {agent_type.upper()}",
            "data": {"selected_agent": agent_type}
        })

        if agent_type == "debugging":
            res = self.debugging_agent.diagnose_and_fix(error_message=message, context=problem_context)
        elif agent_type == "math":
            res = self.math_agent.calculate_and_prove(problem=message, context=problem_context)
        elif agent_type == "research":
            res = self.research_agent.research(topic=message, context=problem_context)
        elif agent_type == "tutor":
            res = self.tutor_agent.explain_or_hint(prompt=message, context=problem_context)
        elif agent_type == "verifier":
            res = self.verifier_agent.verify_solution(original_problem=problem_context or message, proposed_solution=message)
        else: # coding
            res = self.coding_agent.solve(prompt=message, code_context=problem_context)

        activity_steps.extend(res.get("activity_steps", []))
        primary_answer = res.get("final_answer", "")

        # Optional Verification Step for coding and debugging solutions
        if verify_result and agent_type in ["coding", "debugging"] and len(primary_answer) > 50:
            activity_steps.append({
                "step": "Verification Review",
                "description": "Verifier Agent auditing proposed solution for correctness and edge cases."
            })
            audit_res = self.verifier_agent.verify_solution(original_problem=message, proposed_solution=primary_answer)
            activity_steps.extend(audit_res.get("activity_steps", []))

        return {
            "response": primary_answer,
            "agent_type": agent_type,
            "agent_role": res.get("agent_role", f"{agent_type.capitalize()} Agent"),
            "activity_steps": activity_steps,
            "provider": type(self.provider).__name__
        }

