from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class MemoryType(str, Enum):
    SKILL_EVIDENCE = "skill_evidence"
    KNOWLEDGE_GAP = "knowledge_gap"
    EXPRESSION_PATTERN = "expression_pattern"
    MISCONCEPTION = "misconception"
    GROWTH = "growth"

class CandidateMemoryItem(BaseModel):
    """Structured longitudinal candidate memory item."""
    memory_id: str
    candidate_id: str
    type: MemoryType
    topic: str
    skill: Optional[str] = None
    level: Optional[int] = Field(default=None, description="Depth level achieved (1 to 6)")
    evidence: str = Field(description="Concrete evidence summary or observed pattern")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    source_interview: str = Field(description="Interview session ID where evidence was recorded")
    status: str = Field(default="active", description="active, resolved, or superseded")
    pattern: Optional[str] = None
    previous_level: Optional[int] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GrowthEvent(BaseModel):
    """Detected candidate growth between interviews."""
    candidate_id: str
    topic: str
    previous_level: int
    current_level: int
    growth: int
    confidence: float
    evidence: str
    source_interviews: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PersistentGap(BaseModel):
    """Recurring technical gap observed across multiple interviews."""
    candidate_id: str
    topic: str
    skill: str
    occurrences_count: int
    evidence_samples: List[str]
    source_interviews: List[str]
    status: str = Field(default="active", description="active or resolved")

class MemoryContext(BaseModel):
    """Memory context injected into Interview Planner & Report Engine."""
    candidate_id: str
    total_previous_interviews: int = 0
    recent_memories: List[CandidateMemoryItem] = Field(default_factory=list)
    demonstrated_strengths: List[CandidateMemoryItem] = Field(default_factory=list)
    recurring_gaps: List[PersistentGap] = Field(default_factory=list)
    growth_history: List[GrowthEvent] = Field(default_factory=list)
    unresolved_misconceptions: List[CandidateMemoryItem] = Field(default_factory=list)
    expression_patterns: List[str] = Field(default_factory=list)
    summary_hypothesis: str = Field(default="Baseline candidate interview (No prior memory).")
