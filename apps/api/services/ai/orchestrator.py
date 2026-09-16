import os
import logging
from sqlalchemy.orm import Session
from models.problem import Problem
from models.ai_investigation import (
    AIInvestigation, InvestigationStatus, AIFinding,
    ProblemClarification, AIProposedSolution, AICriticReview, AIAction
)
from .agents.intake import IntakeAgent
from .agents.clarification import ClarificationAgent
from .agents.diagnostic import DiagnosticAgent
from .agents.solution import SolutionAgent
from .agents.critic import CriticAgent

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    key = os.environ.get("AI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
    environment = os.environ.get("ENVIRONMENT", "development")
    if not key and environment == "production":
        raise ValueError("AI_API_KEY is required in production.")
    if not key:
        logger.warning("AI_API_KEY not set — AI investigation will fail gracefully.")
    return key


class InvestigationOrchestrator:
    def __init__(self, db: Session, investigation_id: str):
        self.db = db
        self.investigation_id = investigation_id

        api_key = _get_api_key()
        self.intake_agent = IntakeAgent(api_key=api_key)
        self.clarification_agent = ClarificationAgent(api_key=api_key)
        self.diagnostic_agent = DiagnosticAgent(api_key=api_key)
        self.solution_agent = SolutionAgent(api_key=api_key)
        self.critic_agent = CriticAgent(api_key=api_key)


    def _log_action(self, action_type: str):
        action = AIAction(investigation_id=self.investigation_id, action_type=action_type)
        self.db.add(action)
        self.db.commit()

    def run_cycle(self):
        inv = self.db.query(AIInvestigation).filter(AIInvestigation.id == self.investigation_id).first()
        if not inv:
            return

        try:
            problem_text = f"{inv.problem.title}\n{inv.problem.description}"
            
            if inv.status == InvestigationStatus.CREATED:
                self._run_intake(inv, problem_text)
                
            if inv.status == InvestigationStatus.ANALYZING:
                self._run_clarification(inv, problem_text)
                
            if inv.status == InvestigationStatus.WAITING_FOR_USER:
                # Need to check if user answered all clarifications
                unanswered = [c for c in inv.clarifications if not c.answer]
                if not unanswered:
                    inv.status = InvestigationStatus.RESEARCHING # Skip researching for now -> Diagnosing
                    self.db.commit()
                    
            if inv.status == InvestigationStatus.RESEARCHING:
                # Research Agent would run here. Skip for this iteration.
                inv.status = InvestigationStatus.DIAGNOSING
                self.db.commit()
                
            if inv.status == InvestigationStatus.DIAGNOSING:
                self._run_diagnostic(inv, problem_text)
                
            if inv.status == InvestigationStatus.GENERATING:
                self._run_solutions(inv, problem_text)
                
            if inv.status == InvestigationStatus.REVIEWING:
                self._run_critic(inv, problem_text)
                
            if inv.status == InvestigationStatus.READY:
                # Ready for user review
                pass

        except Exception as e:
            inv.status = InvestigationStatus.FAILED
            inv.error_message = str(e)
            self.db.commit()

    def _run_intake(self, inv: AIInvestigation, problem_text: str):
        self._log_action("INTAKE_START")
        out = self.intake_agent.analyze(problem_text)
        
        # We can store the intake result as a finding, or attach it to the investigation somehow.
        finding = AIFinding(
            investigation_id=inv.id,
            finding=out.summary,
            confidence=1.0,
            evidence="Initial extraction",
            source="IntakeAgent"
        )
        self.db.add(finding)
        
        inv.status = InvestigationStatus.ANALYZING
        self.db.commit()
        self._log_action("INTAKE_COMPLETE")

    def _run_clarification(self, inv: AIInvestigation, problem_text: str):
        self._log_action("CLARIFICATION_START")
        
        # Get intake data
        intake = [f.finding for f in inv.findings if f.source == "IntakeAgent"]
        prev_clarifications = [{"q": c.question, "a": c.answer} for c in inv.clarifications if c.answer]
        
        out = self.clarification_agent.clarify(problem_text, {"intake": intake}, prev_clarifications)
        
        if out.is_information_sufficient or not out.questions:
            inv.status = InvestigationStatus.RESEARCHING
        else:
            for q in out.questions:
                # check if question already asked
                exists = any(c.question == q.question for c in inv.clarifications)
                if not exists:
                    clar = ProblemClarification(
                        investigation_id=inv.id,
                        question=q.question
                    )
                    self.db.add(clar)
            inv.status = InvestigationStatus.WAITING_FOR_USER
            
        self.db.commit()
        self._log_action("CLARIFICATION_COMPLETE")

    def _run_diagnostic(self, inv: AIInvestigation, problem_text: str):
        self._log_action("DIAGNOSTIC_START")
        intake = [f.finding for f in inv.findings if f.source == "IntakeAgent"]
        clars = [{"q": c.question, "a": c.answer} for c in inv.clarifications if c.answer]
        
        out = self.diagnostic_agent.diagnose(problem_text, {"intake": intake}, clars)
        
        for f in out.findings:
            finding = AIFinding(
                investigation_id=inv.id,
                finding=f.finding,
                confidence=f.confidence,
                evidence=f.evidence,
                source=f.source or "DiagnosticAgent"
            )
            self.db.add(finding)
            
        inv.status = InvestigationStatus.GENERATING
        self.db.commit()
        self._log_action("DIAGNOSTIC_COMPLETE")

    def _run_solutions(self, inv: AIInvestigation, problem_text: str):
        self._log_action("SOLUTION_START")
        findings = [{"finding": f.finding, "evidence": f.evidence} for f in inv.findings]
        
        out = self.solution_agent.generate_solutions(problem_text, findings)
        
        for s in out.solutions:
            sol = AIProposedSolution(
                investigation_id=inv.id,
                title=s.title,
                description=s.description,
                steps=s.steps,
                confidence=s.confidence
            )
            self.db.add(sol)
            
        inv.status = InvestigationStatus.REVIEWING
        self.db.commit()
        self._log_action("SOLUTION_COMPLETE")

    def _run_critic(self, inv: AIInvestigation, problem_text: str):
        self._log_action("CRITIC_START")
        findings = [{"finding": f.finding, "evidence": f.evidence} for f in inv.findings]
        
        for sol in inv.solutions:
            if sol.critic_review:
                continue # already reviewed
            
            sol_dict = {
                "title": sol.title,
                "description": sol.description,
                "steps": sol.steps
            }
            out = self.critic_agent.review(problem_text, findings, sol_dict)
            
            review = AICriticReview(
                solution_id=sol.id,
                is_safe=out.is_safe,
                missing_evidence=out.missing_evidence,
                contradictions=out.contradictions,
                unsafe_instructions=out.unsafe_instructions,
                weak_assumptions=out.weak_assumptions,
                alternative_explanations=out.alternative_explanations
            )
            self.db.add(review)
            
        inv.status = InvestigationStatus.READY
        self.db.commit()
        self._log_action("CRITIC_COMPLETE")

