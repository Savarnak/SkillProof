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

class GrowthItem(BaseModel):
    topic: str
    previousLevel: int
    currentLevel: int
    growthAmount: int
    evidence: str

class ProgressChangeItem(BaseModel):
    topic: str
    previousStatus: str
    currentStatus: str
    changeTag: str  # Improved, Sustained, Needs Practice

class CoachedAnswer(BaseModel):
    questionIndex: int
    questionText: str
    originalAnswer: str
    strengths: List[str] = Field(default_factory=list)
    whatHeldItBack: str
    interviewReadyVersion: str
    deliveryFormulaName: str
    deliveryFormulaSteps: List[str] = Field(default_factory=list)

class MisconceptionInsight(BaseModel):
    topic: str
    misconception: str
    whatsActuallyTrue: str
    howToRememberIt: str
    status: str = "Resolved"

class PersistentGapInsight(BaseModel):
    topic: str
    whyItMatters: str
    whatToPractice: str
    suggestedNextChallenge: str
    isResolved: bool = False

class KnowledgeVsExpressionInsight(BaseModel):
    show: bool = False
    headline: str = ""
    technicalDemonstrated: str = ""
    communicationImpact: str = ""
    howToImprove: str = ""

class ActionPlan(BaseModel):
    nextSteps: List[str] = Field(default_factory=list)

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
    knowledgeVsExpressionInsight: KnowledgeVsExpressionInsight = Field(default_factory=KnowledgeVsExpressionInsight)
    misconceptionsFound: List[MisconceptionItem]
    misconceptionInsights: List[MisconceptionInsight] = Field(default_factory=list)
    profileDivergenceNotes: List[str]
    transferAbility: str
    interviewMode: str = "learning_journey"
    jdRequirementCoverage: List[Dict[str, Any]] = Field(default_factory=list)
    refinementDiffs: List[RefinementDiff]
    coachedAnswers: List[CoachedAnswer] = Field(default_factory=list)
    personalPlaybookFormulas: List[Dict[str, str]]
    isFirstTimeCandidate: bool = True
    growthSummary: List[GrowthItem] = Field(default_factory=list)
    whatChangedSinceLastInterview: List[ProgressChangeItem] = Field(default_factory=list)
    persistentGapInsights: List[PersistentGapInsight] = Field(default_factory=list)
    actionPlan: ActionPlan = Field(default_factory=ActionPlan)
    summaryFeedback: str
