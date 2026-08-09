from pydantic import BaseModel, Field
from typing import List, Optional

class CompletedMission(BaseModel):
    mission_id: str
    day_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    completed_at: str

class LearningSignals(BaseModel):
    demonstrated_strengths: List[str] = Field(default_factory=list)
    known_gaps: List[str] = Field(default_factory=list)
    expression_notes: Optional[str] = None
    suspected_misconceptions: List[str] = Field(default_factory=list)

class Candidate(BaseModel):
    candidate_id: str
    name: str
    email: str
    is_synthetic_demo: bool = True
    background_summary: str
    target_role: str
    completed_missions: List[CompletedMission] = Field(default_factory=list)
    learning_signals: LearningSignals = Field(default_factory=LearningSignals)
