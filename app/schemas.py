from pydantic import BaseModel, Field


class MatchResponse(BaseModel):
    match_score: int = Field(..., ge=0, le=100, description="Overall compatibility score, 0-100.")
    matching_skills: list[str] = Field(default_factory=list, description="Skills present in both the resume and the job description.")
    missing_skills: list[str] = Field(default_factory=list, description="Skills required by the job but not found in the resume.")
    strengths: list[str] = Field(default_factory=list, description="Notable strengths of this resume for this specific role.")
    summary: str = Field(..., description="A short, human-readable verdict explaining the score.")
