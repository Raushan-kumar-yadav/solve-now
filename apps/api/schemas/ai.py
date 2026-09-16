from pydantic import BaseModel, Field
from typing import List, Optional

class IntakeOutput(BaseModel):
    category: str = Field(description="Broad category of the problem")
    subcategory: str = Field(description="Specific subcategory")
    summary: str = Field(description="Concise summary of the problem")
    urgency: str = Field(description="low, normal, high, or critical")

class ClarificationQuestion(BaseModel):
    question: str = Field(description="The specific question to ask the user")
    reasoning: str = Field(description="Why this information is necessary")

class ClarificationOutput(BaseModel):
    is_information_sufficient: bool = Field(description="True if enough info exists to diagnose")
    questions: List[ClarificationQuestion] = Field(description="Questions to ask if info is missing")

class FindingOutput(BaseModel):
    finding: str = Field(description="A distinct factual finding or hypothesis")
    confidence: float = Field(description="0.0 to 1.0 confidence score")
    evidence: str = Field(description="The evidence supporting this finding")
    source: str = Field(description="Where this evidence came from (e.g., 'User Description', 'System Logs')")

class DiagnosticOutput(BaseModel):
    findings: List[FindingOutput] = Field(description="List of diagnostic findings and root causes")

class ProposedSolutionOutput(BaseModel):
    title: str = Field(description="Short title for the solution")
    description: str = Field(description="Detailed explanation of the solution")
    steps: List[str] = Field(description="Step-by-step instructions to apply the solution")
    confidence: float = Field(description="Confidence that this will solve the problem")

class SolutionOutput(BaseModel):
    solutions: List[ProposedSolutionOutput] = Field(description="List of proposed solutions")

class CriticReviewOutput(BaseModel):
    is_safe: bool = Field(description="True if the solution does not recommend destructive/unsafe actions")
    missing_evidence: List[str] = Field(description="Evidence that is missing to support the solution", default=[])
    contradictions: List[str] = Field(description="Contradictions between the solution and the problem description", default=[])
    unsafe_instructions: List[str] = Field(description="Steps that are destructive or unsafe", default=[])
    weak_assumptions: List[str] = Field(description="Assumptions made by the solution that may be false", default=[])
    alternative_explanations: List[str] = Field(description="Other root causes not addressed by the solution", default=[])
