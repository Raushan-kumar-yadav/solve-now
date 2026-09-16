from .base import BaseAgent
from pydantic import BaseModel, Field

class KnowledgeDocumentOutput(BaseModel):
    is_quality_sufficient: bool = Field(description="Does this solution actually solve the problem effectively and comprehensively?")
    title: str = Field(description="A clean, generalized title for this knowledge")
    content: str = Field(description="The finalized, generalized knowledge document, free of any user PII or sensitive data.")
    quality_score: int = Field(description="0-100 score of the solution's quality and clarity")

class KnowledgeAgent(BaseAgent):
    def evaluate_and_draft(self, problem_description: str, solution_content: str, verification_count: int) -> KnowledgeDocumentOutput:
        system_prompt = (
            "You are the Knowledge Agent. Your job is to read a resolved problem and its verified solution, "
            "anonymize it (remove PII/secrets/IP), evaluate its quality, and draft a generalized knowledge document. "
            "If the solution is low quality, incomplete, or a hacky workaround, set is_quality_sufficient to False."
        )
        
        prompt = f"""
        Original Problem: {problem_description}
        Accepted Solution: {solution_content}
        Community Verifications: {verification_count}
        
        Process this into a generalized knowledge base article.
        """
        
        return self.run(prompt, KnowledgeDocumentOutput, system_prompt)

