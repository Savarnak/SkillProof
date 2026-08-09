from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from app.interview.schemas import MisconceptionItem, TopicAssessment

class WeightedScoreBreakdown(BaseModel):
    technicalKnowledge: float = Field(..., ge=0.0, le=1.0)
    reasoning: float = Field(..., ge=0.0, le=1.0)
    application: float = Field(..., ge=0.0, le=1.0)
    expression: float = Field(..., ge=0.0, le=1.0)
    transfer: float = Field(..., ge=0.0, le=1.0)
    overallReadiness: int = Field(..., ge=0, le=100)

class TopicEvidenceExpander(BaseModel):
    topic_id: str
    topic_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidenceCount: int = 0
    sourceQuestions: List[int] = Field(default_factory=list)
    evidenceQuotes: List[str] = Field(default_factory=list)
    statusTag: str = "Demonstrated"  # Strong, Demonstrated, Developing, Insufficient, Not Assessed

class RefinementDiff(BaseModel):
    questionIndex: int
    questionText: str
    originalAnswer: str
    interviewReadyVersion: str
    diffAdditions: List[str] = Field(default_factory=list)
    diffDeletions: List[str] = Field(default_factory=list)
    deliveryFormula: str
    whatWasGood: str
    whatCouldImprove: str

class DiscoveryReportData(BaseModel):
    interviewId: str
    candidateName: str
    curriculumTitle: str
    totalQuestionsAsked: int
    uniqueDaysCovered: int
    weightedScores: WeightedScoreBreakdown
    topicEvidenceExpanders: List[TopicEvidenceExpander]
    demonstratedStrengths: List[str]
    knowledgeGaps: List[str]
    expressionGaps: List[str]
    showKnowledgeVsExpressionInsight: bool
    insightMessage: Optional[str] = None
    misconceptionsFound: List[MisconceptionItem]
    profileDivergenceNotes: List[str]
    transferAbility: str
    interviewMode: str = "learning_journey"
    jdRequirementCoverage: List[Dict[str, Any]] = Field(default_factory=list)
    refinementDiffs: List[RefinementDiff]
    personalPlaybookFormulas: List[Dict[str, str]]
    summaryFeedback: str
