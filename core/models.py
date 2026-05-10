from pydantic import BaseModel, Field
from typing import List

class JobDescription(BaseModel):
    skills: List[str] = Field(description="Key technical and soft skills required")
    experience: str = Field(description="Required experience level and domain")
    qualifications: str = Field(description="Minimum education or certifications")

class DimensionScore(BaseModel):
    score: int = Field(description="Score from 0 to 10")
    justification: str = Field(description="One-line justification explaining the score")

class CandidateEvaluation(BaseModel):
    skills_match: DimensionScore
    experience_relevance: DimensionScore
    education_certs: DimensionScore
    project_portfolio: DimensionScore
    communication_quality: DimensionScore
