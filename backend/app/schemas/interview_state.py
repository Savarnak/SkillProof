from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class SkillDepthLevel(str, Enum):
    RECOGNITION = "Recognition"
    UNDERSTANDING = "Understanding"
    APPLICATION = "Application"
    ENGINEERING = "Engineering"
    SYSTEM_DESIGN = "System Design"
    TRANSFER = "Transfer"

class AdaptiveAction(str, Enum):
    GO_DEEPER = "Go deeper"
    PROBE_MISSING = "Probe missing concept"
    REPHRASE = "Rephrase"
    SCAFFOLD = "Recover/scaffold"
    CHANGE_TOPIC = "Change topic"
    CROSS_DOMAIN = "Cross-domain transfer"

class SessionStatus(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class SkillAssessment(BaseModel):
    topic: str
    knowledge: float = Field(..., ge=0.0, le=1.0)
    expression: float = Field(..., ge=0.0, le=1.0)
    application: float = Field(..., ge=0.0, le=1.0)
    depth_level: SkillDepthLevel = SkillDepthLevel.RECOGNITION
    evidence: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)

class QuestionAnswerTurn(BaseModel):
    turn_index: int
    day_id: str
    topic_id: str
    depth_level: SkillDepthLevel
    question_text: str
    candidate_answer: Optional[str] = None
    next_action: Optional[AdaptiveAction] = None
    scaffold_used: Optional[str] = None
    misconception_flagged: Optional[str] = None
    turn_analysis: Optional[str] = None

class DeterministicState(BaseModel):
    min_questions: int = 8
    min_curriculum_days: int = 4
    total_questions_asked: int = 0
    covered_days: List[str] = Field(default_factory=list)
    covered_topics: List[str] = Field(default_factory=list)
    meets_completion_criteria: bool = False

class InterviewSession(BaseModel):
    session_id: str
    candidate_id: str
    curriculum_id: str
    status: SessionStatus = SessionStatus.INITIALIZED
    current_turn_index: int = 0
    turns: List[QuestionAnswerTurn] = Field(default_factory=list)
    assessments: Dict[str, SkillAssessment] = Field(default_factory=dict)
    deterministic_state: DeterministicState = Field(default_factory=DeterministicState)
    created_at: str
    updated_at: str
