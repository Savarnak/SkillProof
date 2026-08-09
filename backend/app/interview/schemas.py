from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum, IntEnum

class SkillDepthLevel(IntEnum):
    RECOGNITION = 1
    UNDERSTANDING = 2
    APPLICATION = 3
    ENGINEERING = 4
    SYSTEM_DESIGN = 5
    TRANSFER = 6

class AdaptiveAction(str, Enum):
    GO_DEEPER = "GO_DEEPER"
    PROBE = "PROBE"
    REPHRASE = "REPHRASE"
    RECOVER = "RECOVER"
    EXPRESSION_SCAFFOLD = "EXPRESSION_SCAFFOLD"
    CHANGE_TOPIC = "CHANGE_TOPIC"
    TRANSFER = "TRANSFER"
    END = "END"

class TopicStatus(str, Enum):
    NOT_STARTED = "not_started"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"
    SUFFICIENT_EVIDENCE = "sufficient_evidence"
    MASTERED = "mastered"

class MisconceptionStatus(str, Enum):
    IDENTIFIED = "identified"
    PROBED = "probed"
    RESOLVED = "resolved"
    PERSISTS = "persists"

class SessionStatus(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class MisconceptionItem(BaseModel):
    topic: str
    misconception: str
    status: MisconceptionStatus = MisconceptionStatus.IDENTIFIED
    detected_at_turn: int
    resolution_turn: Optional[int] = None

class EvidenceConfidence(BaseModel):
    score: float = Field(0.0, ge=0.0, le=1.0)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    evidenceCount: int = 0
    sourceQuestions: List[int] = Field(default_factory=list)

class TopicAssessment(BaseModel):
    topic_id: str
    topic_name: str
    day_id: str
    day_number: int
    knowledge: float = Field(0.0, ge=0.0, le=1.0)
    expression: float = Field(0.0, ge=0.0, le=1.0)
    application: float = Field(0.0, ge=0.0, le=1.0)
    depth: int = Field(1, ge=1, le=6)
    status: TopicStatus = TopicStatus.NOT_STARTED
    evidence: List[str] = Field(default_factory=list)
    pending_evidence_list: List[str] = Field(default_factory=list)
    knowledge_confidence: float = Field(0.0, ge=0.0, le=1.0)
    expression_confidence: float = Field(0.0, ge=0.0, le=1.0)
    expression_recovery_used: bool = False
    misconceptions: List[str] = Field(default_factory=list)

class AnswerEvaluation(BaseModel):
    technicalCorrectness: float = Field(..., ge=0.0, le=1.0)
    conceptualDepth: float = Field(..., ge=0.0, le=1.0)
    relevance: float = Field(..., ge=0.0, le=1.0)
    reasoning: float = Field(..., ge=0.0, le=1.0)
    application: float = Field(..., ge=0.0, le=1.0)
    expressionClarity: float = Field(..., ge=0.0, le=1.0)
    answerStructure: float = Field(..., ge=0.0, le=1.0)
    confidenceOfAssessment: float = Field(..., ge=0.0, le=1.0)
    
    strengths: List[str] = Field(default_factory=list)
    missingConcepts: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    expressionIssues: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    
    isStrugglingOrDontKnow: bool = False
    isExpressionUnclear: bool = False
    recommendedNextAction: AdaptiveAction = AdaptiveAction.GO_DEEPER
    recommendedReasonCode: str = "evaluated_response"

class InterviewDecision(BaseModel):
    action: AdaptiveAction
    topic_id: str
    target_depth: int
    reasonCode: str
    scaffold_prompt: Optional[str] = None
    transfer_domain: Optional[str] = None

class QuestionTurn(BaseModel):
    turn_index: int
    question_id: str
    topic_id: str
    day_id: str
    day_number: int
    depth_level: int
    question_text: str
    candidate_answer: Optional[str] = None
    evaluation: Optional[AnswerEvaluation] = None
    decision: Optional[InterviewDecision] = None
    timestamp: str

class InterviewState(BaseModel):
    interviewId: str
    candidateId: str
    curriculumId: str
    questionCount: int = 0
    curriculumDaysCovered: List[int] = Field(default_factory=list)
    coveredDayIds: List[str] = Field(default_factory=list)
    topicsAssessed: Dict[str, TopicAssessment] = Field(default_factory=dict)
    currentTopic: str = ""
    currentDayId: str = ""
    currentDepth: int = 1
    conversationHistory: List[QuestionTurn] = Field(default_factory=list)
    skillEvidence: List[str] = Field(default_factory=list)
    pendingEvidence: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    knowledgeGaps: List[str] = Field(default_factory=list)
    expressionGaps: List[str] = Field(default_factory=list)
    misconceptions: List[MisconceptionItem] = Field(default_factory=list)
    transferChallengesUsed: List[str] = Field(default_factory=list)
    profileVsEvidenceDivergence: List[str] = Field(default_factory=list)
    eventLogs: List[Dict[str, Any]] = Field(default_factory=list)
    interviewStatus: SessionStatus = SessionStatus.INITIALIZED
    
    # Deterministic Rule Thresholds
    minQuestions: int = 8
    minCurriculumDays: int = 4
    maxQuestions: int = 15
    canConclude: bool = False
    
    created_at: str
    updated_at: str

class InterviewReport(BaseModel):
    interviewId: str
    candidateName: str
    curriculumTitle: str
    totalQuestionsAsked: int
    uniqueDaysCovered: int
    overallKnowledgeScore: float
    overallExpressionScore: float
    demonstratedStrengths: List[str]
    knowledgeGaps: List[str]
    expressionGaps: List[str]
    misconceptionsFound: List[MisconceptionItem]
    profileDivergenceNotes: List[str]
    topicSummaries: Dict[str, TopicAssessment]
    transferAbility: str
    answerRefinementSuggestions: List[Dict[str, str]]
    summaryFeedback: str
